"""Create tenant-scoped subscriptions and feature flags."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260828_0010'
down_revision = '20260827_0009'
branch_labels = None
depends_on = None

TENANT_TABLES = (
    'tenant_subscriptions',
    'plan_features',
    'tenant_feature_overrides',
)


def enable_tenant_rls(table: str) -> None:
    op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY {table}_tenant_isolation ON {table} '
        "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def tenant_id_column(uuid: sa.types.TypeEngine[object]) -> sa.Column[object]:
    return sa.Column(
        'organization_id',
        uuid,
        sa.ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False,
    )


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'tenant_subscriptions',
        tenant_id_column(uuid),
        sa.Column('plan_key', sa.String(50), nullable=False, server_default='starter'),
        sa.Column('status', sa.String(24), nullable=False, server_default='trialing'),
        sa.Column('provider', sa.String(50), nullable=False, server_default='local'),
        sa.Column('external_reference', sa.String(255)),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True)),
        sa.Column('current_period_starts_at', sa.DateTime(timezone=True)),
        sa.Column('current_period_ends_at', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "status in ('trialing', 'active', 'past_due', 'cancelled', 'suspended')",
            name='ck_tenant_subscriptions_status',
        ),
        sa.PrimaryKeyConstraint('organization_id'),
    )
    op.create_table(
        'plan_features',
        tenant_id_column(uuid),
        sa.Column('plan_key', sa.String(50), nullable=False),
        sa.Column('feature_key', sa.String(100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint('organization_id', 'plan_key', 'feature_key'),
    )
    op.create_table(
        'tenant_feature_overrides',
        tenant_id_column(uuid),
        sa.Column('feature_key', sa.String(100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint('organization_id', 'feature_key'),
    )
    for table in TENANT_TABLES:
        enable_tenant_rls(table)


def downgrade() -> None:
    for table in reversed(TENANT_TABLES):
        op.drop_table(table)
