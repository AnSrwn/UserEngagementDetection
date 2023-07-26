from typing import List, Optional
from database.models import Engagement
from database.repositories.base_repositories import GenericSqlRepository
from database.repositories.engagement.engagement_repository import (
    EngagementRepositoryBase,
)
from datetime import datetime
from sqlmodel import Session, select, delete


class EngagementRepository(GenericSqlRepository[Engagement], EngagementRepositoryBase):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Engagement)

    def list_raw_by_datetime(
        self, from_datetime: Optional[datetime], to_datetime: Optional[datetime]
    ) -> List[Engagement]:
        statement = select(self._model_cls)
        if from_datetime != None:
            statement = statement.where(self._model_cls.time > from_datetime)
        if to_datetime != None:
            statement = statement.where(self._model_cls.time < to_datetime)

        result = self._session.exec(statement).all()
        result.sort(key=lambda x: x.time)
        return result

    def deleteAll(self) -> int:
        statement = delete(self._model_cls)
        result = self._session.exec(statement)
        return result.rowcount
