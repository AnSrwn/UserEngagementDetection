from abc import ABC, abstractmethod
from typing import Optional
from database.models import Engagement
from database.repositories.base_repositories import GenericRepository


class EngagementRepositoryBase(GenericRepository[Engagement], ABC):
    @abstractmethod
    def get_by_peer_connection(self, peer_conncection: str) -> Optional[Engagement]:
        raise NotImplementedError()
