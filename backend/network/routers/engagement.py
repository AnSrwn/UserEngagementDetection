import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from fastapi import APIRouter

from database.database_service import DatabaseService
from database.models import Engagement
from network.models.engagement import EngagementSimple
from network.routers.webrtc import peerConnections

log = logging.getLogger("uvicorn.debug")

router = APIRouter()


class EngagementType(Enum):
    BOREDOM = "boredom"
    ENGAGEMENT = "engagement"
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

        engagement_per_client: dict[str, List[Engagement]] = await get_engagement_per_client(raw_engagement)
        average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = await get_average_per_client(
            engagement_per_client)
        simple_engagement: EngagementSimple = await get_simple_engagement(average_per_client)

        return simple_engagement


    async def get_simple_engagement(average_per_client):
        simple_engagement = EngagementSimple()
        simple_engagement.connections = len(peerConnections)
        simple_engagement.visible_users = len(average_per_client)
        for key, value in average_per_client.items():
            await add_engagement_level(simple_engagement, value, EngagementType.BOREDOM)
            await add_engagement_level(simple_engagement, value, EngagementType.ENGAGEMENT)
            await add_engagement_level(simple_engagement, value, EngagementType.CONFUSION)
            await add_engagement_level(simple_engagement, value, EngagementType.FRUSTRATION)
        return simple_engagement


    async def add_engagement_level(simple_engagement, value, engagement_type: EngagementType):
        key = None
        if engagement_type == EngagementType.BOREDOM:
            key = simple_engagement.boredom
        elif engagement_type == EngagementType.ENGAGEMENT:
            key = simple_engagement.engagement
        elif engagement_type == EngagementType.CONFUSION:
            key = simple_engagement.confusion
        elif engagement_type == EngagementType.FRUSTRATION:
            key = simple_engagement.frustration

        if value[engagement_type] == EngagementLevel.HIGH:
            key.high += 1
        elif value[engagement_type] == EngagementLevel.MIDDLE:
            key.middle += 1
        elif value[engagement_type] == EngagementLevel.LOW:
            key.low += 1


    async def get_engagement_per_client(raw_engagement):
        engagement_per_client: dict[str, List[Engagement]] = {}
        for raw_engagement in raw_engagement:
            if not (raw_engagement.peer_connection in engagement_per_client):
                engagement_per_client[raw_engagement.peer_connection] = []
            engagement_per_client[raw_engagement.peer_connection].append(raw_engagement)
        return engagement_per_client


    async def get_average_per_client(engagement_per_client):
        average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = {}
        for key, value in engagement_per_client.items():
            sum_boredom = sum_engagement = sum_confusion = sum_frustration = 0
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
            average_per_client[key] = {EngagementType.BOREDOM: setEngagementLevel(avg_boredom),
                                       EngagementType.ENGAGEMENT: setEngagementLevel(avg_engagement),
                                       EngagementType.CONFUSION: setEngagementLevel(avg_confusion),
                                       EngagementType.FRUSTRATION: setEngagementLevel(avg_frustration)}
        return average_per_client


    @router.delete("/engagement/", response_model=int)
    async def delete_engagement():
        return db_service.engagement.deleteAll()
