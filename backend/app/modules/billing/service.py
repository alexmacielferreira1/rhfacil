from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def has_feature(
    connection: AsyncConnection,
    organization_id: UUID,
    feature_key: str,
) -> bool:
    enabled = await connection.scalar(
        text(
            """
            select coalesce(feature_override.enabled, plan_feature.enabled, false)
            from tenant_subscriptions as subscription
            left join plan_features as plan_feature
              on plan_feature.organization_id = subscription.organization_id
             and plan_feature.plan_key = subscription.plan_key
             and plan_feature.feature_key = :feature_key
            left join tenant_feature_overrides as feature_override
              on feature_override.organization_id = subscription.organization_id
             and feature_override.feature_key = :feature_key
            where subscription.organization_id = :organization_id
              and (
                subscription.status = 'active'
                or (
                    subscription.status = 'trialing'
                    and subscription.trial_ends_at is not null
                    and subscription.trial_ends_at > now()
                )
              )
            """
        ),
        {'organization_id': organization_id, 'feature_key': feature_key},
    )
    return enabled is True
