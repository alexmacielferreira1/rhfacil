from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class PrivacyRequestCreate(BaseModel):
    request_type: Literal['access', 'correction', 'deletion', 'portability', 'review']


class PrivacyRequestCreated(BaseModel):
    id: UUID
    status: str = 'pending'


class PrivacyRequestUpdate(BaseModel):
    status: Literal['pending', 'in_progress', 'completed', 'rejected']
    notes: str | None = None


class PrivacyRequestUpdated(BaseModel):
    id: UUID
    status: str
