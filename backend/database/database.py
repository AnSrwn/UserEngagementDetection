from typing import Callable
from sqlmodel import create_engine
from config.config import settings
from sqlmodel import Session
from sqlmodel.pool import StaticPool


def create_sqlmodel_engine():
    return create_engine(settings.db_url, poolclass=StaticPool)


def sqlmodel_session_maker(engine) -> Callable[[], Session]:
    return lambda: Session(bind=engine, autocommit=False, autoflush=False)
