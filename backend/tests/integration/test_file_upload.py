from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.integration.auth_support import OWNER_URL, authenticated_client


@pytest.mark.asyncio
async def test_authenticated_upload_is_stored_with_random_name_in_quarantine(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv('UPLOAD_ROOT', str(tmp_path))
    async with authenticated_client(monkeypatch) as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/files',
            files={'file': ('../../report.txt', b'safe report', 'text/plain')},
            headers={'X-CSRF-Token': csrf},
        )
        assert response.status_code == 201, response.json()

        owner = create_async_engine(OWNER_URL)
        try:
            async with owner.connect() as connection:
                stored = (
                    await connection.execute(
                        text(
                            'select original_name, storage_key, media_type, size_bytes, status '
                            'from stored_files where id = :file_id'
                        ),
                        {'file_id': response.json()['id']},
                    )
                ).one()
        finally:
            await owner.dispose()

    assert response.json()['status'] == 'quarantined'
    assert stored.original_name == 'report.txt'
    assert stored.media_type == 'text/plain'
    assert stored.size_bytes == 11
    assert stored.status == 'quarantined'
    stored_path = tmp_path / stored.storage_key
    assert stored_path.read_bytes() == b'safe report'
    assert stored_path.name != 'report.txt'


@pytest.mark.asyncio
async def test_upload_rejects_disallowed_content_type(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv('UPLOAD_ROOT', str(tmp_path))
    async with authenticated_client(monkeypatch) as context:
        csrf = context.login.cookies['saas_csrf']
        response = await context.client.post(
            '/api/v1/files',
            files={'file': ('payload.exe', b'MZ', 'application/x-msdownload')},
            headers={'X-CSRF-Token': csrf},
        )
    assert response.status_code == 415
    assert list(tmp_path.rglob('*')) == []


@pytest.mark.asyncio
async def test_download_is_blocked_until_file_becomes_available(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv('UPLOAD_ROOT', str(tmp_path))
    async with authenticated_client(monkeypatch) as context:
        csrf = context.login.cookies['saas_csrf']
        uploaded = await context.client.post(
            '/api/v1/files',
            files={'file': ('report.txt', b'safe report', 'text/plain')},
            headers={'X-CSRF-Token': csrf},
        )
        file_id = uploaded.json()['id']

        quarantined = await context.client.get(f'/api/v1/files/{file_id}')
        assert quarantined.status_code == 409

        reviewed = await context.client.post(
            f'/api/v1/files/{file_id}/review',
            json={'verdict': 'clean', 'details': 'Revisão local aprovada.'},
            headers={'X-CSRF-Token': csrf},
        )
        assert reviewed.status_code == 200, reviewed.json()

        downloaded = await context.client.get(f'/api/v1/files/{file_id}')
        assert downloaded.status_code == 200
        assert downloaded.content == b'safe report'
        assert downloaded.headers['content-type'].startswith('text/plain')
        assert 'report.txt' in downloaded.headers['content-disposition']
