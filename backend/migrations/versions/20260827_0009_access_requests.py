"""Create tenant access links and approval requests."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260827_0009'
down_revision = '20260827_0008'
branch_labels = None
depends_on = None

TENANT_TABLES = ('organization_access_links', 'access_requests')


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
        'organization_access_links',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        'access_requests',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('name', sa.String(160)),
        sa.Column('reason', sa.String(1000)),
        sa.Column('status', sa.String(24), nullable=False, server_default='pending'),
        sa.Column('decision_by_user_id', uuid, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('decision_reason', sa.String(1000)),
        sa.Column('decided_at', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "status in ('pending', 'approved', 'rejected', 'expired', 'cancelled')",
            name='ck_access_requests_status',
        ),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_access_requests_pending_email "
        "ON access_requests (organization_id, lower(email)) WHERE status = 'pending'"
    )
    op.create_index(
        'ix_access_requests_tenant_created',
        'access_requests',
        ['organization_id', 'created_at'],
    )
    for table in TENANT_TABLES:
        enable_tenant_rls(table)
    op.execute(
        """
        CREATE FUNCTION resolve_access_tenant(candidate_hash text)
        RETURNS uuid
        LANGUAGE sql
        SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
            SELECT link.organization_id
            FROM public.organization_access_links AS link
            WHERE link.token_hash = candidate_hash
              AND link.active
              AND (link.expires_at IS NULL OR link.expires_at > now())
            LIMIT 1
        $$
        """
    )
    op.execute('REVOKE ALL ON FUNCTION resolve_access_tenant(text) FROM PUBLIC')
    op.execute('GRANT EXECUTE ON FUNCTION resolve_access_tenant(text) TO gestao_de_funcionarios_app')


def downgrade() -> None:
    op.execute('DROP FUNCTION resolve_access_tenant(text)')
    op.drop_index('ix_access_requests_tenant_created', table_name='access_requests')
    op.execute('DROP INDEX uq_access_requests_pending_email')
    op.drop_table('access_requests')
    op.drop_table('organization_access_links')
