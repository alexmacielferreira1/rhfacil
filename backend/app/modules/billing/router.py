from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authorization import authorize_role
from app.core.tenant import set_tenant
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import CurrentUser
from app.modules.billing.schemas import FeatureState, SubscriptionAdministration

router = APIRouter(prefix='/billing', tags=['billing administration'])


@router.get('/subscription', response_model=SubscriptionAdministration)
async def get_subscription_administration(
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> SubscriptionAdministration:
    authorize_role(user.role, {'owner', 'admin'})
    engine: AsyncEngine = request.app.state.db_engine
    async with engine.begin() as connection:
        await set_tenant(connection, user.organization_id)
        subscription = (
            await connection.execute(
                text(
                    """
                    select plan_key, status, provider, trial_ends_at, current_period_ends_at
                    from tenant_subscriptions
                    where organization_id = :tenant
                    """
                ),
                {'tenant': user.organization_id},
            )
        ).mappings().one_or_none()
        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Assinatura não configurada.',
            )

        feature_rows = (
            await connection.execute(
                text(
                    """
                    select
                        coalesce(feature_override.feature_key, plan_feature.feature_key) as key,
                        coalesce(feature_override.enabled, plan_feature.enabled, false) as enabled,
                        case when feature_override.feature_key is null
                            then 'plan' else 'override' end as source
                    from plan_features as plan_feature
                    full outer join tenant_feature_overrides as feature_override
                      on feature_override.organization_id = plan_feature.organization_id
                     and feature_override.feature_key = plan_feature.feature_key
                    where coalesce(
                        feature_override.organization_id,
                        plan_feature.organization_id
                    ) = :tenant
                      and (plan_feature.plan_key = :plan_key or plan_feature.plan_key is null)
                    order by key
                    """
                ),
                {'tenant': user.organization_id, 'plan_key': subscription['plan_key']},
            )
        ).mappings()
        await record_audit_event(
            connection,
            organization_id=user.organization_id,
            actor_user_id=user.user_id,
            event_type='billing.subscription.viewed',
            target_type='tenant_subscription',
            target_id=str(user.organization_id),
        )

        return SubscriptionAdministration(
            **subscription,
            features=[FeatureState.model_validate(row) for row in feature_rows],
        )
