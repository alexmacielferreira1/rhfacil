from pydantic import BaseModel


class OperationalMetrics(BaseModel):
    active_members: int
    pending_access_requests: int
    pending_jobs: int
    quarantined_files: int
    ai_tokens_this_month: int
