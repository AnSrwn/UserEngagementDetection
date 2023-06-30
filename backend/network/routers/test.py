from typing import List
from database.database import create_sqlmodel_engine
from database.database_service import DatabaseService
from database.models import Test
from fastapi import APIRouter

router = APIRouter()

with DatabaseService() as db_service:
    @router.post("/test/", response_model=Test)
    async def add_test(test: Test):
        db_service.test.add(test)
        db_service.commit()
        return test


    @router.get("/test/", response_model=List[Test])
    async def get_test():
        return db_service.test.list()
