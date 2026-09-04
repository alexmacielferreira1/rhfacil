"""Create the template schema marker."""

import sqlalchemy as sa
from alembic import op

revision = '20260826_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'app_schema_version',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'installed_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table('app_schema_version')
