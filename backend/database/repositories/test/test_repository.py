from abc import ABC
from abc import ABC, abstractmethod
from typing import Optional
from database.models import Test
from database.repositories.base_repositories import GenericRepository


class TestRepositoryBase(GenericRepository[Test], ABC):
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Test]:
        raise NotImplementedError()
