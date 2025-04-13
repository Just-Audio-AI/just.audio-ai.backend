import os
from collections.abc import AsyncGenerator
from typing import Annotated

import firebase_admin
from fastapi import Depends
from firebase_admin import App as FirebaseApp
from firebase_admin import credentials
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.client.mail_client import MailClient
from src.client.s3_client import S3Client
from src.client.whisper_ai_client import WhisperAIClient
from src.repository.payment.user_payment_repository import UserPaymentRepository
from src.repository.products_repository import ProductsRepository
from src.repository.user_file_repository import UserFileRepository
from src.repository.user_repository import UserRepository
from src.service.audio_convert_service import AudioConvertService
from src.service.auth import AuthService
from src.service.file_service import FileService
from src.service.payment.user_payment import UserPaymentService
from src.service.products_service import ProductsService
from src.service.user_file_service import UserFileService
from src.settings import settings

db_url = os.environ.get("DATABASE_URL")
db_pool_size = int(os.environ.get("DB_POOL_SIZE", 1))
db_max_overflow = int(os.environ.get("DB_MAX_OVERFLOW", 10))

engine = create_async_engine(
    db_url, pool_size=db_pool_size, max_overflow=db_max_overflow
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session


DB = Annotated[AsyncSession, Depends(get_session)]


async def get_s3_client() -> S3Client:
    return S3Client(
        bucket_name="public-file",
        access_key="minioadmin",
        secret_key="minioadmin",
        service_url="http://0.0.0.0:8000",
        s3_url="127.0.0.1:9000",
    )


async def get_file_service(
    s3_client: Annotated[S3Client, Depends(get_s3_client)]
) -> FileService:
    return FileService(s3_client=s3_client)


async def get_user_file_repository(db: DB) -> UserFileRepository:
    return UserFileRepository(db=db)


async def get_user_file_service(
    user_file_repository: Annotated[
        UserFileRepository, Depends(get_user_file_repository)
    ]
) -> UserFileService:
    return UserFileService(user_file_repository=user_file_repository)


async def get_audio_ai_client() -> WhisperAIClient:
    return WhisperAIClient(
        base_url=settings.WISPER_AI_BASE_URL,
        auth_token=settings.WISPER_AI_AUTH_TOKEN,
    )


async def get_audio_convert_service(
    audio_ai_client: Annotated[WhisperAIClient, Depends(get_audio_ai_client)]
) -> AudioConvertService:
    return AudioConvertService(
        audio_ai_client=audio_ai_client,
    )


async def get_firebase_client() -> FirebaseApp:
    try:
        return firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("src/config/firebase-credentials.json")
        return firebase_admin.initialize_app(cred)


async def get_user_repository(db: DB) -> UserRepository:
    return UserRepository(db=db)


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    firebase_client: FirebaseApp = Depends(get_firebase_client),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        settings=settings,
        firebase_client=firebase_client,
        mail_client=MailClient(settings=settings),
    )


async def get_products_repository(db: DB) -> ProductsRepository:
    return ProductsRepository(db=db)


async def get_products_service(
    products_repository: Annotated[ProductsRepository, Depends(get_products_repository)]
) -> ProductsService:
    return ProductsService(products_repository=products_repository)


async def get_user_payment_repository(db: DB) -> UserPaymentRepository:
    return UserPaymentRepository(db=db)

async def get_user_payment_service(
    user_payment_repository: Annotated[UserPaymentRepository, Depends(get_user_payment_repository)]
):
    return UserPaymentService(user_payment_repository=user_payment_repository)
