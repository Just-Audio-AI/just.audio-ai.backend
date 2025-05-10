from src.client.s3_client import S3Client
from src.repository.user_file_repository import UserFileRepository
from src.service.file_service import FileService
from src.service.user_file_service import UserFileService
from src.dependency import null_pool_async_session


class UserFileServiceFacade:
    @staticmethod
    async def get_user_file_service() -> UserFileService:
        return UserFileService(
            user_file_repository=UserFileRepository(db=null_pool_async_session())
        )


class FileServiceFacade:

    @staticmethod
    async def get_file_service() -> FileService:
        return FileService(
            s3_client=S3Client(
                bucket_name="public-file",
                access_key="minioadmin",
                secret_key="minioadmin",
                service_url="http://app:8000",
                s3_url="minio:9000",
            )
        )
