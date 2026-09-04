from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class FeatureState(BaseModel):
    key: str
    enabled: bool
    source: Literal['plan', 'override']


class SubscriptionAdministration(BaseModel):
    plan_key: str
    status: str
    provider: str
    trial_ends_at: datetime | None
    current_period_ends_at: datetime | None
    features: list[FeatureState]
