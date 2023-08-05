from pydantic import BaseModel


class EngagementDistribution(BaseModel):
    high: int = 0
    middle: int = 0
    low: int = 0


class EngagementSimple(BaseModel):
    connections: int = 0
    visible_users: int = 0
    boredom: EngagementDistribution = EngagementDistribution()
    engagement: EngagementDistribution = EngagementDistribution()
    confusion: EngagementDistribution = EngagementDistribution()
    frustration: EngagementDistribution = EngagementDistribution()
