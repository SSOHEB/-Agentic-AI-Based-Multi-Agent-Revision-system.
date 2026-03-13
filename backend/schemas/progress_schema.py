from pydantic import BaseModel


class DashboardResponse(BaseModel):
    retention_percent: int
    trend: str
    exam_readiness: int
    topics_total: int
    topics_graduated: int
