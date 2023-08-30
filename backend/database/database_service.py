from abc import ABC, abstractmethod

from common.log import Logger
from database.database import create_sqlmodel_engine, sqlmodel_session_maker
from database.repositories.engagement.engagement_repository import (EngagementRepositoryBase, )
from database.repositories.engagement.engagement_repository_impl import (EngagementRepository, )
from sqlmodel import SQLModel


# How to use: https://github.com/manukanne/sqlmodel-repository-pattern/blob/main/main.py


class DatabaseServiceBase(ABC):
    engagement: EngagementRepositoryBase

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
        return super().__enter__()

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self._engine)
        Logger.instance().info("Database created")

    def commit(self):
        self._session.commit()

    def close(self):
        self._session.close()

    def rollback(self):
        self._session.rollback()
