"""Create the tenant-safe employee core (People/Employees module)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260904_0011"
down_revision = "20260828_0010"
branch_labels = None
depends_on = None

TENANT_TABLES = ("employees",)


def tenant_column(uuid: sa.types.TypeEngine[object]) -> sa.Column[object]:
    return sa.Column(
        "organization_id",
        uuid,
        sa.ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )


def timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    ]


def enable_tenant_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY {table}_tenant_isolation ON {table} "
        "USING (organization_id = "
        "nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = "
        "nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)

    op.create_table(
        "employees",
        sa.Column("id", uuid, nullable=False, server_default=sa.text("gen_random_uuid()")),
        tenant_column(uuid),
        sa.Column("full_name", sa.String(180), nullable=False),
        sa.Column("normalized_email", sa.String(320), nullable=False),
        sa.Column("job_title", sa.String(120), nullable=False),
        sa.Column("department", sa.String(120), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("admission_date", sa.Date(), nullable=False),
        sa.Column("termination_date", sa.Date()),
        *timestamps(),
        sa.CheckConstraint(
            "status in ('active', 'inactive', 'terminated')",
            name="ck_employees_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "id"),
        sa.UniqueConstraint(
            "organization_id", "normalized_email", name="uq_employees_email_tenant"
        ),
    )
    op.create_index(
        "ix_employees_tenant_status",
        "employees",
        ["organization_id", "status"],
    )

    for table in TENANT_TABLES:
        enable_tenant_rls(table)


def downgrade() -> None:
    for table in reversed(TENANT_TABLES):
        op.drop_table(table)
