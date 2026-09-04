"""Restrict runtime database role."""

from alembic import op

revision = '20260826_0003'
down_revision = '20260826_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
    op.execute('GRANT USAGE ON SCHEMA public TO gestao_de_funcionarios_app')
    op.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gestao_de_funcionarios_app')
    op.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gestao_de_funcionarios_app')
    op.execute(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
        'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gestao_de_funcionarios_app'
    )
    op.execute(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
        'GRANT USAGE, SELECT ON SEQUENCES TO gestao_de_funcionarios_app'
    )


def downgrade() -> None:
    op.execute(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
        'REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM gestao_de_funcionarios_app'
    )
    op.execute(
        'REVOKE SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public '
        'FROM gestao_de_funcionarios_app'
    )
    op.execute('REVOKE USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public FROM gestao_de_funcionarios_app')
