from dataclasses import dataclass

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


@dataclass
class UserRepository:
    db: AsyncSession

    async def delete_user(self, user_id: int) -> None:
        async with self.db as session:
            await session.execute(delete(User).where(User.id == user_id))
            await session.commit()
            await session.flush()

    async def get_user_by_firebase_token(self, firebase_token: str) -> User | None:
        async with self.db as session:
            query = select(User).where(User.firebase_token == firebase_token)
            return (await session.execute(query)).scalar_one_or_none()

    async def create_user_by_firebase_token(self, firebase_token: str, email: str | None = None) -> User:
        async with self.db as session:
            if email:
                user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
                if user is None:
                    return await self._create_and_get_user_by_firebase(firebase_token)
                else:
                    user.firebase_token = firebase_token
                    await session.commit()
                    await session.flush()
                    return user
            else:
                return await self._create_and_get_user_by_firebase(firebase_token)

    async def _create_and_get_user_by_firebase(self, firebase_token: str) -> User:
        async with self.db as session:
            query = insert(User).values(firebase_token=firebase_token).returning(User.id)
            user_id = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            await session.flush()
            return await self.get_user_by_id_or_none(user_id)

    async def get_user_by_id_or_none(self, user_id: int) -> User | None:
        async with self.db as session:
            query = select(User).where(User.id == user_id)
            return (await session.execute(query)).scalar_one_or_none()
