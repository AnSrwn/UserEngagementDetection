from typing import List, Optional
from database.models import Engagement
from database.database_service import DatabaseService
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

with DatabaseService() as db_service:

    @router.get("/engagement/", response_model=List[Engagement])
    async def get_test(from_datetime: datetime = None, to_datetime: datetime = None):
        return db_service.engagement.list_by_datetime(from_datetime, to_datetime)
