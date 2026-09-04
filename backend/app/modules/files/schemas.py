from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class StoredFileCreated(BaseModel):
    id: UUID
    status: str = 'quarantined'


class FileReview(BaseModel):
    verdict: Literal['clean', 'malicious']
    details: str = Field(min_length=1, max_length=500)
