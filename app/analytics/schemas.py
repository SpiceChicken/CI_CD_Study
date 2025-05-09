from pydantic import BaseModel
from datetime import datetime

class ClickLogInfo(BaseModel):
    short_code: str
    timestamp: datetime
    client_ip: str | None
    user_agent: str | None

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    total_clicks: int
    logs: list[ClickLogInfo]