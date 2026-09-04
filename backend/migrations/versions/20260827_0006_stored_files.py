"""Create tenant-scoped file metadata with quarantine status."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260827_0006'
down_revision = '20260827_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'stored_files',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column(
            'organization_id',
            uuid,
            sa.ForeignKey('organizations.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('owner_user_id', uuid, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('original_name', sa.String(255), nullable=False),
        sa.Column('storage_key', sa.String(255), nullable=False, unique=True),
        sa.Column('media_type', sa.String(150), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('sha256', sa.String(64), nullable=False),
        sa.Column('status', sa.String(24), nullable=False, server_default='quarantined'),
        sa.Column('scan_result', sa.String(255)),
        sa.Column('available_at', sa.DateTime(timezone=True)),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint('size_bytes >= 0', name='ck_stored_files_nonnegative_size'),
        sa.CheckConstraint(
            "status in ('quarantined', 'available', 'rejected')",
            name='ck_stored_files_status',
        ),
    )
    op.create_index(
        'ix_stored_files_tenant_created',
        'stored_files',
        ['organization_id', 'created_at'],
    )
    op.execute('ALTER TABLE stored_files ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE stored_files FORCE ROW LEVEL SECURITY')
    op.execute(
        "CREATE POLICY stored_files_tenant_isolation ON stored_files "
        "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
        "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
    )


def downgrade() -> None:
    op.drop_index('ix_stored_files_tenant_created', table_name='stored_files')
    op.drop_table('stored_files')
