from typing import List, Optional
from database.models import Engagement
from database.repositories.base_repositories import GenericSqlRepository
from database.repositories.engagement.engagement_repository import (
    EngagementRepositoryBase,
)
from datetime import datetime
from sqlmodel import Session, select


class EngagementRepository(GenericSqlRepository[Engagement], EngagementRepositoryBase):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Engagement)

    def list_by_datetime(
        self, from_datetime: Optional[datetime], to_datetime: Optional[datetime]
    ) -> List[Engagement]:
        enteties = select(self._model_cls)
        if from_datetime != None:
            enteties = enteties.where(self._model_cls.time > from_datetime)
        if to_datetime != None:
            enteties = enteties.where(self._model_cls.time < to_datetime)

        result = self._session.exec(enteties).all()
        result.sort(key=lambda x: x.time)
        return result
