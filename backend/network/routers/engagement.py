import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from fastapi import APIRouter

from common.utils import partition
from database.database_service import DatabaseService
from database.models import Engagement
from network.models.engagement import EngagementSimple, EngagementIntervalAverage
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
    @router.get("/engagement/connections-count")
    async def count_connections():
        """This endpoint is used to retrieve the number of active webRTC connections."""
        return len(peerConnections)


    @router.get("/engagement/raw/period", response_model=List[Engagement])
    async def list_engagement(from_datetime: datetime = None, to_datetime: datetime = None):
        """This endpoint is used to get the raw engagement data, generated by the KI model."""
        return db_service.engagement.list_raw_by_datetime(from_datetime, to_datetime)


    @router.get("/engagement/average/percentage/period", response_model=List[EngagementIntervalAverage])
    async def list_engagement_average_percentage_period(from_datetime: datetime = None, to_datetime: datetime = None,
                                                        interval: int = 5):
        """This endpoint is used to get the average engagement over a time period."""
        average_engagements_per_intervals = []

        if from_datetime is not None:
            from_datetime = from_datetime.replace(microsecond=0)
        if to_datetime is not None:
            to_datetime = to_datetime.replace(microsecond=0)

        raw_engagement = db_service.engagement.list_raw_by_datetime(
            None if from_datetime is None else from_datetime.isoformat(),
            None if to_datetime is None else to_datetime.isoformat())

        engagement_per_intervals = await get_engagement_per_intervals(from_datetime, to_datetime, interval,
                                                                      raw_engagement)

        for value in engagement_per_intervals:
            engagement_per_client: dict[str, List[Engagement]] = await get_engagement_per_client(value)
            average_per_client: dict[str, dict[EngagementType, float]] = await get_average_per_client(
                engagement_per_client)

            engagement_interval_average: EngagementIntervalAverage = await get_interval_average(average_per_client,
                                                                                                min(value, key=lambda
                                                                                                    item: item.time).time,
                                                                                                max(value, key=lambda
                                                                                                    item: item.time).time)

            average_engagements_per_intervals.append(engagement_interval_average)

        return average_engagements_per_intervals


    @router.get("/engagement/average/percentage", response_model=List[EngagementIntervalAverage])
    async def list_engagement_average_percentage(interval: int = 5):
        """This endpoint is used to get the average engagement of the last seconds (interval)"""
        to_datetime = datetime.now()
        from_datetime = to_datetime - timedelta(seconds=interval)

        raw_engagement = db_service.engagement.list_raw_by_datetime(from_datetime.isoformat(), to_datetime.isoformat())

        engagement_per_client: dict[str, List[Engagement]] = await get_engagement_per_client(raw_engagement)
        average_per_client: dict[str, dict[EngagementType, float]] = await get_average_per_client(engagement_per_client)

        engagement_interval_average: EngagementIntervalAverage = await get_interval_average(average_per_client,
                                                                                            from_datetime, to_datetime)

        return [engagement_interval_average]


    @router.get("/engagement/average/simple/period", response_model=List[EngagementSimple])
    async def list_engagement_average_simple_period(from_datetime: datetime = None, to_datetime: datetime = None,
                                                    interval: int = 5):
        """This endpoint is used to get the average engagement over a time period categorized in low,
        middle and high."""
        simple_engagements_per_intervals = []

        if from_datetime is not None:
            from_datetime = from_datetime.replace(microsecond=0)
        if to_datetime is not None:
            to_datetime = to_datetime.replace(microsecond=0)

        raw_engagement = db_service.engagement.list_raw_by_datetime(
            None if from_datetime is None else from_datetime.isoformat(),
            None if to_datetime is None else to_datetime.isoformat())

        engagement_per_intervals = await get_engagement_per_intervals(from_datetime, to_datetime, interval,
                                                                      raw_engagement)

        for value in engagement_per_intervals:
            engagement_per_client: dict[str, List[Engagement]] = await get_engagement_per_client(value)
            average_per_client: dict[str, dict[EngagementType, float]] = await get_average_per_client(
                engagement_per_client)
            simple_average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = to_simple_averages_per_client(
                average_per_client)
            simple_engagement: EngagementSimple = await get_simple_engagement(simple_average_per_client, min(value,
                                                                                                             key=lambda
                                                                                                                 item: item.time).time,
                                                                              max(value,
                                                                                  key=lambda item: item.time).time)
            simple_engagements_per_intervals.append(simple_engagement)

        return simple_engagements_per_intervals


    @router.get("/engagement/average/simple", response_model=List[EngagementSimple])
    async def get_engagement_average_simple(interval: int = 5):
        """This endpoint is used to get the average engagement of the last seconds (interval) categorized in low,
        middle and high."""
        simple_engagements = []

        to_datetime = datetime.now()
        from_datetime = to_datetime - timedelta(seconds=interval)

        raw_engagement = db_service.engagement.list_raw_by_datetime(from_datetime.isoformat(), to_datetime.isoformat())

        engagement_per_intervals = await get_engagement_per_intervals(from_datetime, to_datetime, interval,
                                                                      raw_engagement)

        for value in engagement_per_intervals:
            engagement_per_client: dict[str, List[Engagement]] = await get_engagement_per_client(value)
            average_per_client: dict[str, dict[EngagementType, float]] = await get_average_per_client(
                engagement_per_client)
            simple_average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = to_simple_averages_per_client(
                average_per_client)
            simple_engagement: EngagementSimple = await get_simple_engagement(simple_average_per_client, min(value,
                                                                                                             key=lambda
                                                                                                                 item: item.time).time,
                                                                              max(value,
                                                                                  key=lambda item: item.time).time)
            simple_engagements.append(simple_engagement)

        if len(simple_engagements) > 1:
            simple_engagements = [simple_engagements[0]]

        if len(simple_engagements) < 1:
            simple_engagements = [await get_simple_engagement({}, None, None)]

        return simple_engagements


    @router.delete("/engagement/", response_model=int)
    async def delete_engagement():
        """This endpoint is used to delete all engagement data."""
        return db_service.engagement.deleteAll()


    async def get_engagement_per_intervals(from_datetime, to_datetime, interval, raw_engagement):
        engagement_per_intervals = []

        start_time = from_datetime
        if start_time is None:
            start_time = min(raw_engagement, key=lambda item: item.time).time

        end_time = start_time + timedelta(seconds=interval)
        if to_datetime is None:
            to_datetime = datetime.now()

        while end_time <= to_datetime:
            engagement_interval, raw_engagement = partition(
                lambda item: start_time.replace(tzinfo=None) <= item.time.replace(tzinfo=None) < end_time.replace(
                    tzinfo=None), raw_engagement)
            if len(engagement_interval) > 0:
                engagement_per_intervals.append(engagement_interval)

            start_time = end_time
            end_time = start_time + timedelta(seconds=interval)

        return engagement_per_intervals


    async def get_interval_average(average_per_client, from_datetime, to_datetime):
        sum_boredom = sum_engagement = sum_confusion = sum_frustration = 0
        engagement_interval_average = EngagementIntervalAverage()
        count = len(average_per_client)
        if count == 0:
            return engagement_interval_average

        for key, value in average_per_client.items():
            sum_boredom += value[EngagementType.BOREDOM]
            sum_engagement += value[EngagementType.ENGAGEMENT]
            sum_confusion += value[EngagementType.CONFUSION]
            sum_frustration += value[EngagementType.FRUSTRATION]

        engagement_interval_average.from_datetime = from_datetime
        engagement_interval_average.to_datetime = to_datetime
        engagement_interval_average.avg_boredom = sum_boredom / count
        engagement_interval_average.avg_engagement = sum_engagement / count
        engagement_interval_average.avg_confusion = sum_confusion / count
        engagement_interval_average.avg_frustration = sum_frustration / count

        return engagement_interval_average


    async def get_simple_engagement(average_per_client, from_datetime, to_datetime):
        simple_engagement = EngagementSimple()
        simple_engagement.connections = len(peerConnections)
        simple_engagement.visible_users = len(average_per_client)
        simple_engagement.from_datetime = from_datetime
        simple_engagement.to_datetime = to_datetime
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


    async def get_engagement_per_client(raw_engagement: List[Engagement]):
        engagement_per_client: dict[str, List[Engagement]] = {}
        for raw_engagement in raw_engagement:
            if not (raw_engagement.peer_connection in engagement_per_client):
                engagement_per_client[raw_engagement.peer_connection] = []
            engagement_per_client[raw_engagement.peer_connection].append(raw_engagement)
        return engagement_per_client


    async def get_average_per_client(engagement_per_client):
        average_per_client: dict[str, dict[EngagementType, float]] = {}
        for key, value in engagement_per_client.items():
            sum_boredom = sum_engagement = sum_confusion = sum_frustration = 0
            for item in value:
                sum_boredom += item.boredom
                sum_engagement += item.engagement
                sum_confusion += item.confusion
                sum_frustration += item.frustration

            count = len(value)
            avg_boredom = sum_boredom / count
            avg_engagement = sum_engagement / count
            avg_confusion = sum_confusion / count
            avg_frustration = sum_frustration / count
            average_per_client[key] = {EngagementType.BOREDOM: round(avg_boredom, 2),
                                       EngagementType.ENGAGEMENT: round(avg_engagement, 2),
                                       EngagementType.CONFUSION: round(avg_confusion, 2),
                                       EngagementType.FRUSTRATION: round(avg_frustration, 2)}
        return average_per_client


    def to_simple_averages_per_client(average_engagement_per_client):
        average_per_client: dict[str, dict[EngagementType, EngagementLevel]] = {}
        for key, value in average_engagement_per_client.items():
            average_per_client[key] = {EngagementType.BOREDOM: setEngagementLevel(value[EngagementType.BOREDOM]),
                                       EngagementType.ENGAGEMENT: setEngagementLevel(value[EngagementType.ENGAGEMENT]),
                                       EngagementType.CONFUSION: setEngagementLevel(value[EngagementType.CONFUSION]),
                                       EngagementType.FRUSTRATION: setEngagementLevel(
                                           value[EngagementType.FRUSTRATION])}
        return average_per_client
