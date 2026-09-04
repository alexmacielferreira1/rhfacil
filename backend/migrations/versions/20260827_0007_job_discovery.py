"""Expose minimal pending-job tenant discovery to the runtime worker."""

from alembic import op

revision = '20260827_0007'
down_revision = '20260827_0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION pending_job_tenants()
        RETURNS TABLE (organization_id uuid)
        LANGUAGE sql
        SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
            SELECT DISTINCT jobs.organization_id
            FROM public.outbox_jobs AS jobs
            WHERE jobs.status = 'pending' AND jobs.available_at <= now()
            ORDER BY jobs.organization_id
        $$
        """
    )
    op.execute('REVOKE ALL ON FUNCTION pending_job_tenants() FROM PUBLIC')
    op.execute('GRANT EXECUTE ON FUNCTION pending_job_tenants() TO gestao_de_funcionarios_app')


def downgrade() -> None:
    op.execute('DROP FUNCTION pending_job_tenants()')
