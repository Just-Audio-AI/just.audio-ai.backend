import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from random import choices
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException, status
from firebase_admin import App as FirebaseApp
from firebase_admin import auth
from firebase_admin.auth import (
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
)

from src.client.mail_client import MailClient
from src.exceptions import CodeExpiredExceptions, CodeNotFoundExceptions
from src.repository.user_repository import UserRepository
from src.schemas.user import UserCreate, UserTokenResponse
from src.settings import Settings


@dataclass
class AuthService:
    user_repository: UserRepository
    settings: Settings
    mail_client: MailClient
    firebase_client: FirebaseApp

    async def auth_by_firebase_token(self, token: str) -> UserTokenResponse:
        import os

        os.environ["TZ"] = "Europe/London"
        try:
            decoded_token = auth.verify_id_token(
                id_token=token, app=self.firebase_client
            )
            user_uid = decoded_token.get("uid")
            if not user_uid:
                raise ValueError("UID not found in Firebase token")

            # Безопасное получение email
            decoded_email = self._extract_email_from_token(decoded_token)

            if exists_user := await self.user_repository.get_user_by_firebase_token(
                user_uid
            ):
                access_token = await self._create_token(exists_user.id)
                return UserTokenResponse(
                    user_id=exists_user.id,
                    access_token=access_token.get("access_token"),
                )

            user = await self.user_repository.create_user_by_firebase_token(
                user_uid, email=decoded_email, name=decoded_token.get("name")
            )
            return UserTokenResponse(
                user_id=user.id,
                access_token=(await self._create_token(user.id)).get("access_token"),
            )

        except (InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Firebase token: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}",
            )

    def _extract_email_from_token(self, decoded_token: dict) -> Optional[str]:
        """
        Safely extract email from Firebase token
        """
        try:
            identities = decoded_token.get("firebase", {}).get("identities", {})
            emails = identities.get("email", [])
            return emails[0] if emails else None
        except (KeyError, IndexError):
            return None

    async def verify_auth_code(self, email: str, code: int) -> dict:
        code = str(code)
        if code_with_email_link := await self.user_repository.get_code_with_email(
            email, code
        ):
            utc_now = datetime.now(tz=UTC)
            if code_with_email_link.code != code:
                raise CodeNotFoundExceptions
            if code_with_email_link.expires_at < utc_now.replace(tzinfo=None):
                raise CodeExpiredExceptions

            user_id = await self.get_or_create_user(user=UserCreate(email=email))
            access_token = await asyncio.gather(
                *[
                    self._create_token(user_id),
                    self.user_repository.delete_all_email_codes(email),
                ]
            )

            return {
                "user_id": user_id,
                "access_token": access_token[0].get("access_token"),
            }

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
        access_token_expires = timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
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
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.token_secret,
            algorithm=self.settings.token_algorithm,
        )
        return encoded_jwt

    @staticmethod
    async def __generate_random_code() -> str:
        random_number = "".join(choices("0123456789", k=4))
        return random_number

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Проверка JWT токена и возврат payload
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.token_secret,
                algorithms=[self.settings.token_algorithm],
            )

            # Проверка, что токен не просрочен
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has no expiration",
                )

            exp_datetime = datetime.fromtimestamp(exp, tz=UTC)
            if datetime.now(tz=UTC) >= exp_datetime:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
                )

            # Проверка типа токена
            if payload.get("sub") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            return payload

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_user_by_id(self, user_id: int) -> bool:
        """
        Проверка существования пользователя по ID
        """
        user = await self.user_repository.get_user_by_id_or_none(user_id)
        if user is None:
            return False
        return True
