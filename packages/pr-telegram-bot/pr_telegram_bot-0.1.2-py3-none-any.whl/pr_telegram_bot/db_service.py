from abc import ABC, abstractmethod

from .models import User


class UserDBService(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    async def update_user(self, user_id: int, update_data: dict) -> User:
        pass


class InMemoryUserDBService(UserDBService):
    def __init__(self) -> None:
        self.db: dict[int, User] = {}

    async def create_user(self, user: User) -> User:
        self.db[user.id] = user
        return user

    async def get_user(self, user_id: int) -> User | None:
        return self.db.get(user_id)

    async def update_user(self, user_id: int, **update_data: dict) -> User:
        user = self.db[user_id]
        for key, value in update_data.items():
            setattr(user, key, value)
        return user
