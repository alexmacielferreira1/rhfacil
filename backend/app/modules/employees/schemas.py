from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

EmployeeStatus = Literal["active", "inactive", "terminated"]
ContractType = Literal["clt", "pj", "estagio", "temporario", "outro"]

CONTRACT_TYPE_LABELS: dict[ContractType, str] = {
    "clt": "CLT",
    "pj": "PJ",
    "estagio": "Estágio",
    "temporario": "Temporário",
    "outro": "Outro",
}


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    job_title: str = Field(min_length=2, max_length=120)
    department: str = Field(min_length=2, max_length=120)
    admission_date: date
    manager_id: UUID | None = None
    contract_type: ContractType | None = None
    level: str | None = Field(default=None, max_length=60)
    cost_center: str | None = Field(default=None, max_length=60)
    salary_amount: Decimal | None = Field(default=None, ge=0, decimal_places=2, max_digits=12)

    @field_validator("full_name", "job_title", "department")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return normalize_text(value)

    @field_validator("level", "cost_center")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return normalize_text(value) if value else None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    job_title: str | None = Field(default=None, min_length=2, max_length=120)
    department: str | None = Field(default=None, min_length=2, max_length=120)
    manager_id: UUID | None = None
    contract_type: ContractType | None = None
    level: str | None = Field(default=None, max_length=60)
    cost_center: str | None = Field(default=None, max_length=60)
    salary_amount: Decimal | None = Field(default=None, ge=0, decimal_places=2, max_digits=12)

    @field_validator("full_name", "job_title", "department")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return normalize_text(value) if value is not None else None

    @field_validator("level", "cost_center")
    @classmethod
    def clean_optional_extra_text(cls, value: str | None) -> str | None:
        return normalize_text(value) if value else None


class EmployeeStatusChange(BaseModel):
    status: EmployeeStatus
    termination_date: date | None = None


class EmployeeView(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    job_title: str
    department: str
    status: EmployeeStatus
    admission_date: date
    termination_date: date | None
    manager_id: UUID | None
    manager_name: str | None
    contract_type: ContractType | None
    level: str | None
    cost_center: str | None
    salary_amount: Decimal | None
    created_at: datetime
    updated_at: datetime


class EmployeeImportRowResult(BaseModel):
    row_number: int
    email: str
    outcome: Literal["created", "updated", "error"]
    detail: str | None = None


class EmployeeImportSummary(BaseModel):
    created: int
    updated: int
    errors: int
    rows: list[EmployeeImportRowResult]
