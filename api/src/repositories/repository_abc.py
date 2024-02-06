from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Iterable, Optional, Awaitable

T = TypeVar('T')
ID = TypeVar('ID')
IDC = TypeVar('IDC')

class RepositoryABC(ABC, Generic[T, ID, IDC]):

    @abstractmethod
    async def find_all(self, idc: IDC) -> Awaitable[Iterable[T]]:
        pass

    @abstractmethod
    async def find_by_id(self, id: ID, idc: IDC) -> Awaitable[Optional[T]]:
        pass

    @abstractmethod
    async def save(self, t: T, idc: IDC, id: ID) -> Awaitable[Optional[T]]:
        pass

    @abstractmethod
    async def delete_by_id(self, id: ID, idc: IDC) -> Awaitable[None]:
        pass

    @abstractmethod
    async def delete(self, t: T, idc: IDC) -> Awaitable[None]:
        pass

    @abstractmethod
    async def delete_all(self, idc: IDC) -> Awaitable[None]:
        pass

    @abstractmethod
    async def exists_by_id(self, id: ID, idc: IDC) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def exists(self, t: T, idc: IDC) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def count(self, idc: IDC) -> Awaitable[int]:
        pass
