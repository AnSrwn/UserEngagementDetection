from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EngagementDistribution(BaseModel):
    high: int = 0
    middle: int = 0
    low: int = 0


class EngagementSimple(BaseModel):
    connections: int = 0
    visible_users: int = 0
    from_datetime: Optional[datetime]
    to_datetime: Optional[datetime]
    boredom: EngagementDistribution = EngagementDistribution()
    engagement: EngagementDistribution = EngagementDistribution()
    confusion: EngagementDistribution = EngagementDistribution()
    frustration: EngagementDistribution = EngagementDistribution()


class EngagementIntervalAverage(BaseModel):
    from_datetime: Optional[datetime]
    to_datetime: Optional[datetime]
    avg_boredom: float = 0.0
    avg_engagement: float = 0.0
    avg_confusion: float = 0.0
    avg_frustration: float = 0.0
