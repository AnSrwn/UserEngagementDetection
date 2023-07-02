from abc import ABC, abstractmethod
from typing import List, Optional
from database.models import Engagement
from database.repositories.base_repositories import GenericRepository
from datetime import datetime


class EngagementRepositoryBase(GenericRepository[Engagement], ABC):
    @abstractmethod
    def list_by_datetime(
        self, from_datetime: Optional[datetime], to_datetime: Optional[datetime]
    ) -> List[Engagement]:
        raise NotImplementedError()
