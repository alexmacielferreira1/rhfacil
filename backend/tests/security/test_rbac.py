import pytest
from fastapi import HTTPException

from app.core.authorization import authorize_role


def test_owner_is_allowed_when_owner_role_is_required() -> None:
    authorize_role('owner', {'owner'})


def test_member_is_forbidden_when_admin_role_is_required() -> None:
    with pytest.raises(HTTPException) as error:
        authorize_role('member', {'owner', 'admin'})
    assert error.value.status_code == 403
