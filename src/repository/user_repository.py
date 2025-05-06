import datetime as dt
from dataclasses import dataclass

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, UserEmailWithCode
from src.schemas.user import UserCreate


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

    async def create_user_by_firebase_token(
        self, firebase_token: str, name: str | None = None, email: str | None = None
    ) -> User:
        async with self.db as session:
            if email:
                user = (
                    await session.execute(select(User).where(User.email == email))
                ).scalar_one_or_none()
                if user is None:
                    return await self._create_and_get_user_by_firebase(
                        firebase_token, email, name
                    )
                else:
                    user.firebase_token = firebase_token
                    await session.commit()
                    await session.flush()
                    return user
            else:
                return await self._create_and_get_user_by_firebase(
                    firebase_token, name, email
                )

    async def _create_and_get_user_by_firebase(
        self, firebase_token: str, email: str, name: str | None = None
    ) -> User:
        async with self.db as session:
            query = (
                insert(User)
                .values(firebase_token=firebase_token, email=email, name=name)
                .returning(User.id)
            )
            user_id = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            await session.flush()
            return await self.get_user_by_id_or_none(user_id)

    async def create_default_user(self) -> int:
        async with self.db as session:
            query = (
                insert(User)
                .values(
                    username="test_username",
                    email="testemail@gmail.com",
                    avatar="test_avatar",
                    fullname="test_fullname",
                )
                .returning(User.id)
            )
            user_id = (await session.execute(query)).scalar()
            await session.commit()
            await session.flush()
            return user_id

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.db as session:
            query = select(User).where(User.email == email)
            return (await session.execute(query)).scalar()

    async def get_user_by_id_or_none(self, user_id: int) -> User | None:
        async with self.db as session:
            query = select(User).where(User.id == user_id)
            return (await session.execute(query)).scalar_one_or_none()

    async def create_user(self, user: UserCreate) -> int:
        async with self.db as session:
            query = (
                insert(User)
                .values(**user.model_dump(exclude_none=True))
                .returning(User.id)
            )
            res = (await session.execute(query)).scalar()
            await session.commit()
            return res

    async def save_code_with_email(self, email: str, code: str) -> None:
        async with self.db as session:
            await session.execute(delete(UserEmailWithCode).where(UserEmailWithCode.email == email))
            expires_at = dt.datetime.now(tz=dt.UTC) + dt.timedelta(minutes=25)
            await session.execute(
                insert(UserEmailWithCode).values(
                    email=email,
                    code=code,
                    expires_at=expires_at.replace(tzinfo=None),
                )
            )
            await session.commit()
            await session.flush()
            return

    async def get_code_with_email(
        self, email: str, code: str
    ) -> UserEmailWithCode | None:
        async with self.db as session:
            query = select(UserEmailWithCode).where(
                UserEmailWithCode.email == email, UserEmailWithCode.code == code
            )
            return await session.scalar(query)

    async def delete_all_email_codes(self, email: str) -> None:
        async with self.db as session:
            await session.execute(
                delete(UserEmailWithCode).where(UserEmailWithCode.email == email)
            )
            await session.commit()
            await session.flush()
            return
