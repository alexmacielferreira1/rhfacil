from uuid import uuid4

import pytest

from app.modules.billing.providers import BillingProviderUnavailable, DisabledBillingProvider


@pytest.mark.asyncio
async def test_disabled_billing_provider_has_no_external_effect() -> None:
    provider = DisabledBillingProvider()

    with pytest.raises(BillingProviderUnavailable):
        await provider.create_checkout(organization_id=uuid4(), plan_key='starter')
