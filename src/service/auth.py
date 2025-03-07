import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from random import choices

import jwt
from firebase_admin import App as FirebaseApp
from firebase_admin import auth

from src.client.mail_client import MailClient
from src.exceptions import CodeNotFoundExceptions, CodeExpiredExceptions
from src.repository.user_repository import UserRepository
from src.schemas.user import UserCreate
from src.settings import Settings


@dataclass
class AuthService:
    user_repository: UserRepository
    settings: Settings
    mail_client: MailClient
    firebase_client: FirebaseApp

    async def auth_by_firebase_token(self, token: str) -> dict:
        decoded_token = auth.verify_id_token(id_token=token, app=self.firebase_client)
        decoded_email = decoded_token["firebase"]["identities"].get("email")[0]
        user_uid = decoded_token["uid"]

        if exists_user := await self.user_repository.get_user_by_firebase_token(user_uid):
            access_token = await self._create_token(exists_user.id)
            return {"user_id": exists_user.id, "access_token": access_token.get("access_token")}

        user = await self.user_repository.create_user_by_firebase_token(user_uid, email=decoded_email)
        return {"user_id": user.id, "access_token": (await self._create_token(user.id)).get("access_token")}

    async def verify_auth_code(self, email: str, code: int) -> dict:
        if code_with_email_link := await self.user_repository.get_code_with_email(email, code):
            utc_now = datetime.now(tz=None)
            if code_with_email_link.code != code:
                raise CodeNotFoundExceptions
            if code_with_email_link.expires_at.replace(tzinfo=None) < utc_now:
                raise CodeExpiredExceptions

            user_id = await self.get_or_create_user(user=UserCreate(email=email))
            access_token = await asyncio.gather(
                *[self._create_token(user_id), self.user_repository.delete_all_email_codes(email)]
            )

            return {"user_id": user_id, "access_token": access_token[0].get("access_token")}

        raise CodeNotFoundExceptions

    async def get_or_create_user(self, user: UserCreate) -> int:
        if exists_user := await self.user_repository.get_user_by_email(user.email):
            return exists_user.id
        user_id = await self.user_repository.create_user(user)
        return user_id

    async def send_auth_code(self, email: str) -> None:
        code = await self.__generate_random_code()
        await self.mail_client.send_code(code=code, to=email)
        await self.user_repository.save_code_with_email(email, code)

    async def _create_token(self, user_id: int) -> dict:
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": await self._create_access_token(
                data={"user_id": user_id}, expires_delta=access_token_expires
            ),
            "token_type": "Token",
        }

    async def _create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Создание токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(tz=UTC) + expires_delta
        else:
            expire = datetime.now(tz=UTC) + timedelta(minutes=15)
        to_encode.update({"exp": expire, "sub": "access"})
        encoded_jwt = jwt.encode(to_encode, self.settings.token_secret, algorithm=self.settings.token_algorithm)
        return encoded_jwt

    @staticmethod
    async def __generate_random_code() -> int:
        random_number = "".join(choices("0123456789", k=4))
        return int(random_number)
