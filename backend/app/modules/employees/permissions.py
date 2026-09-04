from typing import Literal

from fastapi import HTTPException, status

PeoplePermission = Literal[
    "people:read",
    "people:write",
    "people:manage",
]

ROLE_PERMISSIONS: dict[str, frozenset[PeoplePermission]] = {
    "owner": frozenset({"people:read", "people:write", "people:manage"}),
    "admin": frozenset({"people:read", "people:write", "people:manage"}),
    "member": frozenset({"people:read"}),
}


def authorize_people(role: str, permission: PeoplePermission) -> None:
    if permission not in ROLE_PERMISSIONS.get(role, frozenset()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente.",
        )
