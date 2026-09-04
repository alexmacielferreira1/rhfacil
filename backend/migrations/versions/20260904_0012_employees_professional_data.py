"""Add professional data to employees (manager, contract, salary, level)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260904_0012"
down_revision = "20260904_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)

    op.add_column("employees", sa.Column("manager_id", uuid, nullable=True))
    op.add_column("employees", sa.Column("contract_type", sa.String(20), nullable=True))
    op.add_column("employees", sa.Column("level", sa.String(60), nullable=True))
    op.add_column("employees", sa.Column("cost_center", sa.String(60), nullable=True))
    op.add_column(
        "employees", sa.Column("salary_amount", sa.Numeric(12, 2), nullable=True)
    )

    op.create_check_constraint(
        "ck_employees_contract_type",
        "employees",
        "contract_type in ('clt', 'pj', 'estagio', 'temporario', 'outro')",
    )
    op.create_check_constraint(
        "ck_employees_salary_amount_positive",
        "employees",
        "salary_amount is null or salary_amount >= 0",
    )

    # Gestor precisa ser um colaborador da mesma empresa (mesmo tenant) e não
    # pode ser ele mesmo. A FK composta usa a unique (organization_id, id) já
    # criada na migração anterior para reforçar o isolamento por tenant.
    op.create_foreign_key(
        "fk_employees_manager_same_tenant",
        "employees",
        "employees",
        ["organization_id", "manager_id"],
        ["organization_id", "id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_employees_manager_not_self",
        "employees",
        "manager_id is null or manager_id <> id",
    )
    op.create_index(
        "ix_employees_tenant_manager",
        "employees",
        ["organization_id", "manager_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_employees_tenant_manager", table_name="employees")
    op.drop_constraint("ck_employees_manager_not_self", "employees", type_="check")
    op.drop_constraint("fk_employees_manager_same_tenant", "employees", type_="foreignkey")
    op.drop_constraint("ck_employees_salary_amount_positive", "employees", type_="check")
    op.drop_constraint("ck_employees_contract_type", "employees", type_="check")
    op.drop_column("employees", "salary_amount")
    op.drop_column("employees", "cost_center")
    op.drop_column("employees", "level")
    op.drop_column("employees", "contract_type")
    op.drop_column("employees", "manager_id")
