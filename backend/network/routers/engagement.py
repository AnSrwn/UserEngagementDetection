from typing import List, Optional
from database.models import Engagement
from network.models.engagement import EngagementSimple, EngagementDistribution
from database.database_service import DatabaseService
from datetime import datetime, timedelta
from typing import List
from enum import Enum
from fastapi import APIRouter

router = APIRouter()

class EngagementType(Enum):
    BOREDOM = "boredom"
    ENGAGEMENT= "engagement"
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"

class EngagementLevel(Enum):
    HIGH = 1
    MIDDLE = 2
    LOW = 3

def setEngagementLevel(avg: float) -> EngagementLevel:
    if avg > 66:
        return EngagementLevel.HIGH
    elif avg > 33:
        return EngagementLevel.MIDDLE
    else:
        return EngagementLevel.LOW

with DatabaseService() as db_service:

    @router.get("/engagement/raw", response_model=List[Engagement])
    async def list_engagement(from_datetime: datetime = None, to_datetime: datetime = None):
        return db_service.engagement.list_raw_by_datetime(from_datetime, to_datetime)
    
    @router.get("/engagement/simple", response_model=EngagementSimple)
    async def list_engagement(time_period: int = 5):
        to_datetime = datetime.now()
        from_datetime = to_datetime - timedelta(seconds=time_period)

        raw_engagement = db_service.engagement.list_raw_by_datetime(from_datetime.isoformat(), to_datetime.isoformat())

        engagement_per_client: dict[str, List[Engagement]] = {}

        for raw_engagement in raw_engagement:
            if not (raw_engagement.peer_connection in engagement_per_client):
                engagement_per_client[raw_engagement.peer_connection] = []
            engagement_per_client[raw_engagement.peer_connection].append(raw_engagement)
        
        average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = {}
        for key, value in engagement_per_client.items():
            sum_boredom = 0
            sum_engagement = 0
            sum_confusion = 0
            sum_frustration = 0
            for item in value:
                sum_boredom = sum_boredom + item.boredom
                sum_engagement = sum_engagement + item.engagement
                sum_confusion = sum_confusion + item.confusion
                sum_frustration = sum_frustration + item.frustration

            count = len(value)
            avg_boredom = sum_boredom / count
            avg_engagement = sum_engagement / count
            avg_confusion = sum_confusion / count
            avg_frustration = sum_frustration / count
            average_per_client[key] = {
                EngagementType.BOREDOM: setEngagementLevel(avg_boredom),
                EngagementType.ENGAGEMENT: setEngagementLevel(avg_engagement),
                EngagementType.CONFUSION: setEngagementLevel(avg_confusion),
                EngagementType.FRUSTRATION: setEngagementLevel(avg_frustration)
            }

        simple_engagment = EngagementSimple()
        simple_engagment.users = len(average_per_client)
        for key, value in average_per_client.items():
            if value[EngagementType.BOREDOM] == EngagementLevel.HIGH:
                simple_engagment.boredom.high = simple_engagment.boredom.high + 1
            elif value[EngagementType.BOREDOM] == EngagementLevel.MIDDLE:
                simple_engagment.boredom.middle = simple_engagment.boredom.middle + 1
            elif value[EngagementType.BOREDOM] == EngagementLevel.LOW:
                simple_engagment.boredom.low = simple_engagment.boredom.low + 1

            if value[EngagementType.ENGAGEMENT] == EngagementLevel.HIGH:
                simple_engagment.engagement.high = simple_engagment.engagement.high + 1
            elif value[EngagementType.ENGAGEMENT] == EngagementLevel.MIDDLE:
                simple_engagment.engagement.middle = simple_engagment.engagement.middle + 1
            elif value[EngagementType.ENGAGEMENT] == EngagementLevel.LOW:
                simple_engagment.engagement.low = simple_engagment.engagement.low + 1

            if value[EngagementType.CONFUSION] == EngagementLevel.HIGH:
                simple_engagment.confusion.high = simple_engagment.confusion.high + 1
            elif value[EngagementType.CONFUSION] == EngagementLevel.MIDDLE:
                simple_engagment.confusion.middle = simple_engagment.confusion.middle + 1
            elif value[EngagementType.CONFUSION] == EngagementLevel.LOW:
                simple_engagment.confusion.low = simple_engagment.confusion.low + 1

            if value[EngagementType.FRUSTRATION] == EngagementLevel.HIGH:
                simple_engagment.frustration.high = simple_engagment.frustration.high + 1
            elif value[EngagementType.FRUSTRATION] == EngagementLevel.MIDDLE:
                simple_engagment.frustration.middle = simple_engagment.frustration.middle + 1
            elif value[EngagementType.FRUSTRATION] == EngagementLevel.LOW:
                simple_engagment.frustration.low = simple_engagment.frustration.low + 1

        return simple_engagment
    
    @router.delete("/engagement/", response_model=int)
    async def delete_engagement():
        return db_service.engagement.deleteAll()
