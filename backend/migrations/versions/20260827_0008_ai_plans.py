"""Create tenant plans and privacy-safe AI usage accounting."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260827_0008'
down_revision = '20260827_0007'
branch_labels = None
depends_on = None

TENANT_TABLES = ('tenant_plans', 'ai_usage_events')


def enable_tenant_rls(table: str) -> None:
    op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY {table}_tenant_isolation ON {table} '
        "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'tenant_plans',
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            primary_key=True,
        ),
        sa.Column('plan_key', sa.String(50), nullable=False, server_default='starter'),
        sa.Column('seat_limit', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('storage_limit_bytes', sa.BigInteger(), nullable=False, server_default='104857600'),
        sa.Column('ai_monthly_token_limit', sa.Integer(), nullable=False, server_default='100000'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            'seat_limit > 0 and storage_limit_bytes > 0 and ai_monthly_token_limit >= 0',
            name='ck_tenant_plans_positive_limits',
        ),
    )
    op.create_table(
        'ai_usage_events',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('actor_user_id', uuid, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('provider', sa.String(80), nullable=False),
        sa.Column('model', sa.String(120), nullable=False),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(24), nullable=False),
        sa.Column('error_code', sa.String(80)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            'input_tokens >= 0 and output_tokens >= 0',
            name='ck_ai_usage_nonnegative_tokens',
        ),
        sa.CheckConstraint(
            "status in ('succeeded', 'failed', 'blocked')",
            name='ck_ai_usage_status',
        ),
    )
    op.create_index(
        'ix_ai_usage_tenant_created',
        'ai_usage_events',
        ['organization_id', 'created_at'],
    )
    for table in TENANT_TABLES:
        enable_tenant_rls(table)
    op.execute('REVOKE UPDATE, DELETE ON ai_usage_events FROM gestao_de_funcionarios_app')


def downgrade() -> None:
    op.drop_index('ix_ai_usage_tenant_created', table_name='ai_usage_events')
    op.drop_table('ai_usage_events')
    op.drop_table('tenant_plans')
