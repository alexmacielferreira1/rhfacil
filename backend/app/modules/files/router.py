import asyncio
import hashlib
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.config import get_settings
from app.core.tenant import set_tenant
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser
from app.modules.files.schemas import FileReview, StoredFileCreated

router = APIRouter(prefix='/files', tags=['files'])
ALLOWED_MEDIA_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/webp',
    'text/plain',
}


@router.post('', response_model=StoredFileCreated, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> StoredFileCreated:
    media_type = file.content_type or 'application/octet-stream'
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Tipo de arquivo não permitido.',
        )
    settings = get_settings()
    contents = await file.read(settings.upload_max_bytes + 1)
    if len(contents) > settings.upload_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail='Arquivo excede o limite permitido.',
        )

    file_id = uuid4()
    safe_name = Path((file.filename or 'upload').replace('\\', '/')).name[:255]
    storage_key = Path('quarantine', str(user.organization_id), f'{file_id}.bin')
    destination = settings.upload_root / storage_key
    await asyncio.to_thread(destination.parent.mkdir, parents=True, exist_ok=True)
    await asyncio.to_thread(destination.write_bytes, contents)

    engine: AsyncEngine = request.app.state.db_engine
    try:
        async with engine.begin() as connection:
            await set_tenant(connection, user.organization_id)
            await connection.execute(
                text(
                    """
                    insert into stored_files
                        (id, organization_id, owner_user_id, original_name, storage_key,
                         media_type, size_bytes, sha256)
                    values (:id, :organization_id, :owner_user_id, :original_name, :storage_key,
                            :media_type, :size_bytes, :sha256)
                    """
                ),
                {
                    'id': file_id,
                    'organization_id': user.organization_id,
                    'owner_user_id': user.user_id,
                    'original_name': safe_name,
                    'storage_key': storage_key.as_posix(),
                    'media_type': media_type,
                    'size_bytes': len(contents),
                    'sha256': hashlib.sha256(contents).hexdigest(),
                },
            )
            await record_audit_event(
                connection,
                organization_id=user.organization_id,
                actor_user_id=user.user_id,
                event_type='file.upload.quarantined',
                target_type='stored_file',
                target_id=str(file_id),
            )
    except Exception:
        await asyncio.to_thread(destination.unlink, missing_ok=True)
        raise
    return StoredFileCreated(id=UUID(str(file_id)))


@router.post('/{file_id}/review', response_model=StoredFileCreated)
async def review_file(
    file_id: UUID,
    payload: FileReview,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> StoredFileCreated:
    authorize_role(user.role, {'owner', 'admin'})
    next_status = 'available' if payload.verdict == 'clean' else 'rejected'
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        updated = await connection.scalar(
            text(
                """
                update stored_files
                set status = :status,
                    scan_result = :details,
                    available_at = case
                        when cast(:status as varchar) = 'available' then now()
                        else null
                    end
                where id = :file_id and organization_id = :organization_id
                  and status = 'quarantined'
                returning id
                """
            ),
            {
                'status': next_status,
                'details': payload.details,
                'file_id': file_id,
                'organization_id': user.organization_id,
            },
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Arquivo em quarentena não encontrado.',
            )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type=f'file.review.{payload.verdict}',
            target_type='stored_file',
            target_id=str(file_id),
        )
    return StoredFileCreated(id=file_id, status=next_status)


@router.get('/{file_id}', response_class=FileResponse)
async def download_file(
    file_id: UUID,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> FileResponse:
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        stored = (
            await connection.execute(
                text(
                    """
                    select original_name, storage_key, media_type, status
                    from stored_files
                    where id = :file_id and organization_id = :organization_id
                    """
                ),
                {'file_id': file_id, 'organization_id': user.organization_id},
            )
        ).one_or_none()
        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Arquivo não encontrado.',
            )
        if stored.status != 'available':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Arquivo ainda não está disponível.',
            )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='file.downloaded',
            target_type='stored_file',
            target_id=str(file_id),
        )

    root = get_settings().upload_root.resolve()
    path = (root / stored.storage_key).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Arquivo não encontrado.')
    return FileResponse(
        path=path,
        media_type=stored.media_type,
        filename=stored.original_name,
    )
