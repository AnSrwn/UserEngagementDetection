import logging

from abc import ABC, abstractmethod
from database.repositories.test.test_repository import TestRepositoryBase
from database.database import create_sqlmodel_engine, sqlmodel_session_maker
from database.repositories.engagement.engagement_repository import (
    EngagementRepositoryBase,
)
from database.repositories.engagement.engagement_repository_impl import (
    EngagementRepository,
)
from database.repositories.test.test_repository_impl import TestRepository
from sqlmodel import SQLModel

log = logging.getLogger("uvicorn.debug")

# How to use: https://github.com/manukanne/sqlmodel-repository-pattern/blob/main/main.py


class DatabaseServiceBase(ABC):
    engagement: EngagementRepositoryBase
    test: TestRepositoryBase

    _engine = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError()


class DatabaseService(DatabaseServiceBase):
    def __init__(self) -> None:
        self._engine = create_sqlmodel_engine()
        session_maker = sqlmodel_session_maker(self._engine)
        self._session_factory = session_maker

    def __enter__(self):
        self._session = self._session_factory()
        self.engagement = EngagementRepository(self._session)
        self.test = TestRepository(self._session)
        return super().__enter__()

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self._engine)
        log.info("Database created")

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
