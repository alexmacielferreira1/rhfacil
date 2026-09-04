from uuid import UUID


class BillingProviderUnavailable(Exception):
    """Raised because billing integrations are intentionally disabled in Base V1."""


class DisabledBillingProvider:
    provider_name = 'disabled'

    async def create_checkout(self, *, organization_id: UUID, plan_key: str) -> str:
        del organization_id, plan_key
        raise BillingProviderUnavailable
