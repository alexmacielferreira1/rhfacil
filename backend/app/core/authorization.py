from collections.abc import Set

from fastapi import HTTPException, status


def authorize_role(role: str, allowed_roles: Set[str]) -> None:
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permissão insuficiente.',
        )
