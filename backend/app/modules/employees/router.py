import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.tenant import set_tenant
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user, validate_csrf
from app.modules.auth.schemas import CurrentUser
from app.modules.employees.permissions import authorize_people
from app.modules.employees.schemas import (
    CONTRACT_TYPE_LABELS,
    EmployeeCreate,
    EmployeeImportRowResult,
    EmployeeImportSummary,
    EmployeeStatusChange,
    EmployeeUpdate,
    EmployeeView,
)

router = APIRouter(prefix="/people", tags=["people"])

EMPLOYEE_COLUMNS = """
    e.id, e.full_name, e.normalized_email as email, e.job_title, e.department, e.status,
    e.admission_date, e.termination_date, e.manager_id, m.full_name as manager_name,
    e.contract_type, e.level, e.cost_center, e.salary_amount,
    e.created_at, e.updated_at
"""

EMPLOYEE_FROM = "from employees e left join employees m on m.id = e.manager_id"

CSV_HEADER = [
    "email",
    "full_name",
    "job_title",
    "department",
    "admission_date",
    "contract_type",
    "level",
    "cost_center",
    "salary_amount",
    "manager_email",
]


@router.post("/employees", response_model=EmployeeView, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> EmployeeView:
    authorize_people(user.role, "people:write")
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        row = await _insert_employee(connection, user.organization_id, payload)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um colaborador com este e-mail.",
            )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type="people.employee.created",
            target_type="employee",
            target_id=str(row["id"]),
        )
    return EmployeeView.model_validate(row)


@router.get("/employees", response_model=list[EmployeeView])
async def list_employees(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[EmployeeView]:
    authorize_people(user.role, "people:read")
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        rows = (
            await connection.execute(
                text(
                    f"""
                    select {EMPLOYEE_COLUMNS}
                    {EMPLOYEE_FROM}
                    where e.organization_id = :tenant
                    order by e.created_at desc, e.id desc
                    """
                ),
                {"tenant": user.organization_id},
            )
        ).mappings()
        return [EmployeeView.model_validate(row) for row in rows]


@router.get("/employees/export.csv")
async def export_employees_csv(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> StreamingResponse:
    """Exporta os colaboradores em CSV, pronto para abrir e editar no Excel."""
    authorize_people(user.role, "people:read")
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        rows = (
            await connection.execute(
                text(
                    f"""
                    select {EMPLOYEE_COLUMNS}
                    {EMPLOYEE_FROM}
                    where e.organization_id = :tenant
                    order by e.full_name
                    """
                ),
                {"tenant": user.organization_id},
            )
        ).mappings()
        employees = [EmployeeView.model_validate(row) for row in rows]

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(CSV_HEADER)
    for emp in employees:
        writer.writerow(
            [
                emp.email,
                emp.full_name,
                emp.job_title,
                emp.department,
                emp.admission_date.isoformat(),
                emp.contract_type or "",
                emp.level or "",
                emp.cost_center or "",
                str(emp.salary_amount) if emp.salary_amount is not None else "",
                "",  # manager_email preenchido manualmente por quem revisar a planilha
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=colaboradores.csv"},
    )


@router.post("/employees/import", response_model=EmployeeImportSummary)
async def import_employees_csv(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
    file: UploadFile,
) -> EmployeeImportSummary:
    """Importa/atualiza colaboradores a partir de um CSV (mesmo formato do export)."""
    authorize_people(user.role, "people:manage")
    raw = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw), delimiter=";")

    engine: AsyncEngine = request.app.state.db_engine
    results: list[EmployeeImportRowResult] = []
    created = updated = errors = 0

    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        for row_number, raw_row in enumerate(reader, start=2):
            email = (raw_row.get("email") or "").strip().lower()
            try:
                if not email:
                    raise ValueError("E-mail é obrigatório.")
                salary_raw = (raw_row.get("salary_amount") or "").strip()
                salary = Decimal(salary_raw.replace(",", ".")) if salary_raw else None
                payload = EmployeeCreate(
                    full_name=raw_row.get("full_name", ""),
                    email=email,
                    job_title=raw_row.get("job_title", ""),
                    department=raw_row.get("department", ""),
                    admission_date=raw_row.get("admission_date") or None,
                    contract_type=(raw_row.get("contract_type") or "").strip().lower() or None,
                    level=raw_row.get("level") or None,
                    cost_center=raw_row.get("cost_center") or None,
                    salary_amount=salary,
                )
            except (ValidationError, ValueError, InvalidOperation) as exc:
                errors += 1
                results.append(
                    EmployeeImportRowResult(
                        row_number=row_number, email=email, outcome="error", detail=str(exc)
                    )
                )
                continue

            outcome = await _upsert_employee_row(connection, user.organization_id, payload)
            if outcome == "created":
                created += 1
            else:
                updated += 1
            results.append(
                EmployeeImportRowResult(row_number=row_number, email=email, outcome=outcome)
            )

        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type="people.employee.imported",
            target_type="employee",
            target_id=f"created={created},updated={updated},errors={errors}",
        )

    return EmployeeImportSummary(created=created, updated=updated, errors=errors, rows=results)


@router.get("/employees/{employee_id}", response_model=EmployeeView)
async def get_employee(
    employee_id: UUID,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> EmployeeView:
    authorize_people(user.role, "people:read")
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        row = (
            (
                await connection.execute(
                    text(
                        f"""
                    select {EMPLOYEE_COLUMNS}
                    {EMPLOYEE_FROM}
                    where e.organization_id = :tenant and e.id = :employee_id
                    """
                    ),
                    {"tenant": user.organization_id, "employee_id": employee_id},
                )
            )
            .mappings()
            .one_or_none()
        )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado."
        )
    return EmployeeView.model_validate(row)


@router.patch("/employees/{employee_id}", response_model=EmployeeView)
async def update_employee(
    employee_id: UUID,
    payload: EmployeeUpdate,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> EmployeeView:
    authorize_people(user.role, "people:write")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sem alterações."
        )
    if values.get("manager_id") == employee_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Um colaborador não pode ser gestor de si mesmo.",
        )
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        row = (
            (
                await connection.execute(
                    text(
                        """
                    update employees e
                    set full_name = coalesce(:full_name, full_name),
                        job_title = coalesce(:job_title, job_title),
                        department = coalesce(:department, department),
                        manager_id = coalesce(:manager_id, manager_id),
                        contract_type = coalesce(:contract_type, contract_type),
                        level = coalesce(:level, level),
                        cost_center = coalesce(:cost_center, cost_center),
                        salary_amount = coalesce(:salary_amount, salary_amount),
                        updated_at = now()
                    where organization_id = :tenant and id = :employee_id
                    returning e.id
                    """
                    ),
                    {
                        "tenant": user.organization_id,
                        "employee_id": employee_id,
                        "full_name": values.get("full_name"),
                        "job_title": values.get("job_title"),
                        "department": values.get("department"),
                        "manager_id": values.get("manager_id"),
                        "contract_type": values.get("contract_type"),
                        "level": values.get("level"),
                        "cost_center": values.get("cost_center"),
                        "salary_amount": values.get("salary_amount"),
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado."
            )
        updated_row = (
            (
                await connection.execute(
                    text(
                        f"""
                    select {EMPLOYEE_COLUMNS}
                    {EMPLOYEE_FROM}
                    where e.organization_id = :tenant and e.id = :employee_id
                    """
                    ),
                    {"tenant": user.organization_id, "employee_id": employee_id},
                )
            )
            .mappings()
            .one()
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type="people.employee.updated",
            target_type="employee",
            target_id=str(employee_id),
        )
    return EmployeeView.model_validate(updated_row)


@router.post("/employees/{employee_id}/status", response_model=EmployeeView)
async def change_employee_status(
    employee_id: UUID,
    payload: EmployeeStatusChange,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    _csrf: Annotated[None, Depends(validate_csrf)],
) -> EmployeeView:
    authorize_people(user.role, "people:manage")
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        row = (
            (
                await connection.execute(
                    text(
                        """
                    update employees
                    set status = cast(:target as varchar),
                        termination_date = case
                            when cast(:target as varchar) = 'terminated'
                                then coalesce(:termination_date, current_date)
                            else null
                        end,
                        updated_at = now()
                    where organization_id = :tenant and id = :employee_id
                    returning id
                    """
                    ),
                    {
                        "tenant": user.organization_id,
                        "employee_id": employee_id,
                        "target": payload.status,
                        "termination_date": payload.termination_date,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado."
            )
        updated_row = (
            (
                await connection.execute(
                    text(
                        f"""
                    select {EMPLOYEE_COLUMNS}
                    {EMPLOYEE_FROM}
                    where e.organization_id = :tenant and e.id = :employee_id
                    """
                    ),
                    {"tenant": user.organization_id, "employee_id": employee_id},
                )
            )
            .mappings()
            .one()
        )
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type="people.employee.status_changed",
            target_type="employee",
            target_id=str(employee_id),
        )
    return EmployeeView.model_validate(updated_row)


async def _insert_employee(connection, tenant_id, payload: EmployeeCreate):
    inserted = (
        (
            await connection.execute(
                text(
                    """
                insert into employees
                    (organization_id, full_name, normalized_email, job_title,
                     department, admission_date, manager_id, contract_type,
                     level, cost_center, salary_amount)
                values
                    (:tenant, :full_name, :email, :job_title, :department, :admission_date,
                     :manager_id, :contract_type, :level, :cost_center, :salary_amount)
                on conflict (organization_id, normalized_email) do nothing
                returning id
                """
                ),
                {"tenant": tenant_id, **payload.model_dump(mode="json")},
            )
        )
        .mappings()
        .one_or_none()
    )
    if inserted is None:
        return None
    return (
        (
            await connection.execute(
                text(
                    f"""
                select {EMPLOYEE_COLUMNS}
                {EMPLOYEE_FROM}
                where e.organization_id = :tenant and e.normalized_email = :email
                """
                ),
                {"tenant": tenant_id, "email": payload.email},
            )
        )
        .mappings()
        .one_or_none()
    )


async def _upsert_employee_row(connection, tenant_id, payload: EmployeeCreate) -> str:
    """Cria o colaborador ou atualiza os dados profissionais se o e-mail já existir."""
    row = (
        (
            await connection.execute(
                text(
                    """
                insert into employees
                    (organization_id, full_name, normalized_email, job_title,
                     department, admission_date, contract_type, level, cost_center,
                     salary_amount)
                values
                    (:tenant, :full_name, :email, :job_title, :department, :admission_date,
                     :contract_type, :level, :cost_center, :salary_amount)
                on conflict (organization_id, normalized_email) do update set
                    full_name = excluded.full_name,
                    job_title = excluded.job_title,
                    department = excluded.department,
                    contract_type = coalesce(excluded.contract_type, employees.contract_type),
                    level = coalesce(excluded.level, employees.level),
                    cost_center = coalesce(excluded.cost_center, employees.cost_center),
                    salary_amount = coalesce(excluded.salary_amount, employees.salary_amount),
                    updated_at = now()
                returning (xmax = 0) as inserted
                """
                ),
                {"tenant": tenant_id, **payload.model_dump(mode="json", exclude={"manager_id"})},
            )
        )
        .mappings()
        .one()
    )
    return "created" if row["inserted"] else "updated"


__all__ = ["router", "CONTRACT_TYPE_LABELS"]
