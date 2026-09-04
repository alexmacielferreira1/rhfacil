from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AccessLinkCreated(BaseModel):
    token: str


class PublicAccessRequest(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=160)
    reason: str | None = Field(default=None, max_length=1000)


class AccessRequestAccepted(BaseModel):
    message: str = 'Solicitação recebida para análise.'


class AccessRequestItem(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    reason: str | None
    status: str
    created_at: datetime


class AccessRequestDecision(BaseModel):
    decision: Literal['approved', 'rejected']
    role: Literal['owner', 'admin', 'member'] = 'member'
    reason: str | None = Field(default=None, max_length=1000)


class AccessRequestDecisionResult(BaseModel):
    id: UUID
    status: str
