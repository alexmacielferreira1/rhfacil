"""Create the tenant-scoped persistent outbox queue."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260827_0005'
down_revision = '20260826_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'outbox_jobs',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.Column('idempotency_key', sa.String(200), nullable=False),
        sa.Column('status', sa.String(24), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column(
            'available_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column('locked_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('last_error', sa.Text()),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            'organization_id',
            'idempotency_key',
            name='uq_outbox_jobs_tenant_idempotency',
        ),
        sa.CheckConstraint(
            "status in ('pending', 'processing', 'completed', 'failed')",
            name='ck_outbox_jobs_status',
        ),
        sa.CheckConstraint('attempts >= 0 and max_attempts > 0', name='ck_outbox_jobs_attempts'),
    )
    op.create_index(
        'ix_outbox_jobs_tenant_available',
        'outbox_jobs',
        ['organization_id', 'status', 'available_at'],
    )
    op.execute('ALTER TABLE outbox_jobs ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE outbox_jobs FORCE ROW LEVEL SECURITY')
    op.execute(
        "CREATE POLICY outbox_jobs_tenant_isolation ON outbox_jobs "
        "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def downgrade() -> None:
    op.drop_index('ix_outbox_jobs_tenant_available', table_name='outbox_jobs')
    op.drop_table('outbox_jobs')
