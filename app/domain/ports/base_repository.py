from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]: ...
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]: ...
    @abstractmethod
    async def create(self, obj: T) -> T: ...
    @abstractmethod
    async def update(self, id: int, obj: T) -> Optional[T]: ...
    @abstractmethod
    async def delete(self, id: int) -> bool: ...
