"""Create identity and tenant isolation tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '20260826_0002'
down_revision = '20260826_0001'
branch_labels = None
depends_on = None

TENANT_TABLES = ('memberships', 'invitations', 'user_sessions')


def timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        'organizations',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(160), nullable=False),
        sa.Column('slug', sa.String(80), nullable=False, unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
    )
    op.create_table(
        'users',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(320), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamps(),
    )
    op.create_table(
        'memberships',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', uuid, sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(40), nullable=False, server_default='member'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint('organization_id', 'user_id'),
        *timestamps(),
    )
    op.create_table(
        'invitations',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', uuid, sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('role', sa.String(40), nullable=False, server_default='member'),
        sa.Column('token_hash', sa.String(128), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True)),
        *timestamps(),
    )
    op.create_table(
        'user_sessions',
        sa.Column('id', uuid, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', uuid, sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(128), nullable=False, unique=True),
        sa.Column('csrf_hash', sa.String(128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        *timestamps(),
    )
    for table in TENANT_TABLES:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
        op.execute(
            f"CREATE POLICY {table}_tenant_isolation ON {table} "
            "USING (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid) "
            "WITH CHECK (organization_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)"
        )


def downgrade() -> None:
    for table in reversed(TENANT_TABLES):
        op.drop_table(table)
    op.drop_table('users')
    op.drop_table('organizations')
