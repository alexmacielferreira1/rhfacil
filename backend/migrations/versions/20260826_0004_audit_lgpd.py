"""Create append-only audit and LGPD request tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260826_0004'
down_revision = '20260826_0003'
branch_labels = None
depends_on = None

TENANT_TABLES = ('audit_events', 'data_subject_requests')


def enable_tenant_rls(table: str) -> None:
    op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
    op.execute(
        f"CREATE POLICY {table}_tenant_isolation ON {table} "
        "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'audit_events',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('actor_user_id', uuid, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('target_type', sa.String(100)),
        sa.Column('target_id', sa.String(160)),
        sa.Column(
            'metadata', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column('ip_hash', sa.String(64)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        'ix_audit_events_tenant_created',
        'audit_events',
        ['organization_id', 'created_at'],
    )
    op.create_table(
        'data_subject_requests',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'subject_user_id', uuid, sa.ForeignKey('users.id', ondelete='SET NULL')
        ),
        sa.Column('request_type', sa.String(32), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        sa.Column('notes', sa.Text()),
        sa.Column('due_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "request_type in ('access', 'correction', 'deletion', 'portability', 'review')",
            name='ck_data_subject_request_type',
        ),
        sa.CheckConstraint(
            "status in ('pending', 'in_progress', 'completed', 'rejected')",
            name='ck_data_subject_request_status',
        ),
    )
    for table in TENANT_TABLES:
        enable_tenant_rls(table)

    op.execute('REVOKE UPDATE, DELETE ON audit_events FROM gestao_de_funcionarios_app')


def downgrade() -> None:
    op.drop_table('data_subject_requests')
    op.drop_index('ix_audit_events_tenant_created', table_name='audit_events')
    op.drop_table('audit_events')
