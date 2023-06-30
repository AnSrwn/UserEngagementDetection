from database.models import Test
from database.database import engine
from fastapi import APIRouter
from sqlmodel import Session

router = APIRouter()

@router.post("/test/")
async def add_test(test: Test):
    with Session(engine) as session:
        session.add(test)
        session.commit()
        session.refresh(test)
        return test
    
@router.get("/test/")
async def get_test():
    with Session(engine) as session:
        return session.query(Test).all()
    