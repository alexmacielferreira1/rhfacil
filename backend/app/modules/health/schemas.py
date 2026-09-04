from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal['ok']
    service: str
    environment: str


class ServiceStatuses(BaseModel):
    database: Literal['ok', 'error']
    redis: Literal['ok', 'error']


class ServicesHealthResponse(BaseModel):
    status: Literal['ok', 'error']
    services: ServiceStatuses
