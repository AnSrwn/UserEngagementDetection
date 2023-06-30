from typing import Optional
from database.models import Test
from database.repositories.base_repositories import GenericSqlRepository
from database.repositories.test.test_repository import TestRepositoryBase
from sqlmodel import Session, select


class TestRepository(GenericSqlRepository[Test], TestRepositoryBase):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Test)

    def get_by_name(self, name: str) -> Optional[Test]:
        query = select(Test).where(Test.name == name)
        return self._session.exec(query).first()
