from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    organization: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class AuthResponse(BaseModel):
    status: str = 'ok'


class CurrentUser(BaseModel):
    user_id: UUID
    organization_id: UUID
    email: EmailStr
    role: str


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Literal['owner', 'admin', 'member'] = 'member'


class InvitationCreated(BaseModel):
    token: str


class PendingUserCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    role: Literal['owner', 'admin', 'member'] = 'member'


class InvitationAccept(BaseModel):
    token: str = Field(min_length=43, max_length=200)
    password: str = Field(min_length=12, max_length=256)
