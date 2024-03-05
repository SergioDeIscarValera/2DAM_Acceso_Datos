from abc import abstractmethod
from src.models.user import User
from src.repositories.repository_abc import RepositoryABC

class UserRepositoryABC(RepositoryABC[User, str, str]):
    @abstractmethod
    async def validate_user(self, email: str, password: str) -> bool:
        pass

    @abstractmethod
    async def verify_user(self, email: str, code: str) -> bool:
        pass
