from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlmodel import Session, select, and_
from sqlmodel.sql.expression import SelectOfScalar
from database.models import BaseModel


T = TypeVar("T", bound=BaseModel)


class GenericRepository(Generic[T], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    def list(self, **filters) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def add(self, record: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def update(self, record: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError()


class GenericSqlRepository(GenericRepository[T], ABC):
    def __init__(self, session: Session, model_class: Type[T]) -> None:
        self._session = session
        self._model_cls = model_class

    def _construct_get_stmt(self, id: int) -> SelectOfScalar:
        enteties = select(self._model_cls).where(self._model_cls.id == id)
        return enteties

    def get_by_id(self, id: int) -> Optional[T]:
        enteties = self._construct_get_stmt(id)
        return self._session.exec(enteties).first()

    def _construct_list_stmt(self, **filters) -> SelectOfScalar:
        enteties = select(self._model_cls)
        where_clauses = []
        for column, value in filters.items():
            if not hasattr(self._model_cls, column):
                raise ValueError(f"Invalid column name {column}")
            where_clauses.append(getattr(self._model_cls, column) == value)

        if len(where_clauses) == 1:
            enteties = enteties.where(where_clauses[0])
        elif len(where_clauses) > 1:
            enteties = enteties.where(and_(*where_clauses))
        return enteties

    def list(self, **filters) -> List[T]:
        enteties = self._construct_list_stmt(**filters)
        return self._session.exec(enteties).all()

    def add(self, record: T) -> T:
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return record

    def update(self, record: T) -> T:
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return record

    def delete(self, id: int) -> None:
        record = self.get_by_id(id)
        if record is not None:
            self._session.delete(record)
            self._session.flush()
