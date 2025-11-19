from abc import ABC, abstractmethod
from pymongo.asynchronous.database import AsyncDatabase

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


class MongoUserDBService(UserDBService):
    def __init__(self, db: AsyncDatabase) -> None:
        self._db = db

    async def create_user(self, user: User) -> User:
        await self._db.get_collection("users").insert_one(user.model_dump())
        return user

    async def get_user(self, user_id: int) -> User | None:
        user_doc = await self._db.get_collection("users").find_one({"id": user_id})
        if user_doc:
            return User.model_validate(user_doc)
        return None

    async def update_user(self, user_id: int, **update_data: dict) -> User:
        await self._db.get_collection("users").update_one({"id": user_id}, {"$set": update_data})

