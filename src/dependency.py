import os
from collections.abc import AsyncGenerator
from typing import Annotated

import firebase_admin
import httpx
from fastapi import Depends, HTTPException, status, Request
from firebase_admin import App as FirebaseApp
from firebase_admin import credentials
from openai import OpenAI
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.client.mail_client import MailClient
from src.client.openai_client import OpenAIClient
from src.client.s3_client import S3Client
from src.client.whisper_ai_client import WhisperAIClient
from src.repository.chat_repository import ChatRepository
from src.repository.payment.user_payment_repository import UserPaymentRepository
from src.repository.products_repository import ProductsRepository
from src.repository.user_file_repository import UserFileRepository
from src.repository.user_products_repository import UserProductsRepository
from src.repository.user_repository import UserRepository
from src.service.audio_convert_service import AudioConvertService
from src.service.auth import AuthService
from src.service.chat_service import ChatService
from src.service.file_service import FileService
from src.service.payment.user_payment import UserPaymentService
from src.service.products_service import ProductsService
from src.service.user_file_service import UserFileService
from src.service.user_products_service import UserProductsService
from src.service.user_service import UserService
from src.settings import settings

db_url = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://gen_user:Elf)gVd5wX)Dt@212.60.21.170:5432/audio_ai_prod"
)
db_pool_size = int(os.environ.get("DB_POOL_SIZE", 5))
db_max_overflow = int(os.environ.get("DB_MAX_OVERFLOW", 10))

engine = create_async_engine(
    db_url, pool_size=db_pool_size,
    max_overflow=db_max_overflow,
    pool_pre_ping=True,
)

null_pool_db_engine = create_async_engine(
    db_url,
    poolclass=NullPool,
    echo=False,
    future=True
)
null_pool_async_session = async_sessionmaker(null_pool_db_engine, expire_on_commit=False)
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
        service_url="http://app:8000",
        s3_url="minio:9000",
    )


async def get_file_service(
    s3_client: Annotated[S3Client, Depends(get_s3_client)],
) -> FileService:
    return FileService(s3_client=s3_client)


async def get_user_file_repository(db: DB) -> UserFileRepository:
    return UserFileRepository(db=db)


async def get_user_file_service(
    user_file_repository: Annotated[
        UserFileRepository, Depends(get_user_file_repository)
    ],
) -> UserFileService:
    return UserFileService(user_file_repository=user_file_repository)


async def get_audio_ai_client() -> WhisperAIClient:
    return WhisperAIClient(
        base_url=settings.WISPER_AI_BASE_URL,
        auth_token=settings.WISPER_AI_AUTH_TOKEN,
    )


async def get_audio_convert_service(
    audio_ai_client: Annotated[WhisperAIClient, Depends(get_audio_ai_client)],
    user_file_service: Annotated[UserFileService, Depends(get_user_file_service)]
) -> AudioConvertService:
    return AudioConvertService(
        audio_ai_client=audio_ai_client,
        user_file_service=user_file_service
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
    products_repository: Annotated[
        ProductsRepository, Depends(get_products_repository)
    ],
) -> ProductsService:
    return ProductsService(products_repository=products_repository)


async def get_user_payment_repository(db: DB) -> UserPaymentRepository:
    return UserPaymentRepository(db=db)


async def get_user_products_repository(db: DB) -> UserProductsRepository:
    return UserProductsRepository(db=db)


async def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    user_products_repository: Annotated[
        UserProductsRepository, Depends(get_user_products_repository)
    ],
):
    return UserService(
        user_repository=user_repository,
        user_products_repository=user_products_repository,
    )


async def get_user_products_service(
    user_products_repository: Annotated[
        UserProductsRepository, Depends(get_user_products_repository)
    ],
) -> UserProductsService:
    return UserProductsService(user_products_repository=user_products_repository)


async def get_user_payment_service(
    user_payment_repository: Annotated[
        UserPaymentRepository, Depends(get_user_payment_repository)
    ],
    user_products_service: Annotated[
        UserProductsService, Depends(get_user_products_service)
    ],
    product_repository: Annotated[ProductsRepository, Depends(get_products_repository)],
):
    return UserPaymentService(
        user_payment_repository=user_payment_repository,
        user_products_service=user_products_service,
        product_repository=product_repository,
    )


async def get_current_user_id(
    request: Request, auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> int:
    """
    Проверяет JWT токен в заголовке Authorization и возвращает user_id из токена.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Извлекаем токен из заголовка
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем токен
    payload = await auth_service.verify_token(token)

    # Получаем user_id из payload
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, user_id not found in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем, существует ли пользователь с таким ID
    user_exists = await auth_service.get_user_by_id(user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_chat_repository(db: DB) -> ChatRepository:
    return ChatRepository(db=db)


async def get_openai_client() -> OpenAIClient:
    return OpenAIClient(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        client=OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=httpx.Client(proxy=settings.PROXY_URL)
        ),
    )


async def get_chat_service(
    chat_repository: Annotated[ChatRepository, Depends(get_chat_repository)],
    openai_client: Annotated[OpenAIClient, Depends(get_openai_client)],
    user_products_repository: Annotated[
        UserProductsRepository, Depends(get_user_products_repository)
    ],
    product_repository: Annotated[ProductsRepository, Depends(get_products_repository)],
) -> ChatService:
    return ChatService(
        chat_repository=chat_repository,
        openai_client=openai_client,
        user_products_repository=user_products_repository,
        product_repository=product_repository,
    )
