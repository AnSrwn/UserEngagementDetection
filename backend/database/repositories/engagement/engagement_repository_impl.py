from typing import Optional
from database.models import Engagement
from database.repositories.base_repositories import GenericSqlRepository
from database.repositories.engagement.engagement_repository import (
    EngagementRepositoryBase,
)
from sqlmodel import Session, select


class EngagementRepository(GenericSqlRepository[Engagement], EngagementRepositoryBase):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Engagement)

    def get_by_peer_connection(self, peer_connection: str) -> Optional[Engagement]:
        query = select(Engagement).where(Engagement.peer_connection == peer_connection)
        return self._session.exec(query).first()
