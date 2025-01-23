from dataclasses import dataclass

from fastapi import UploadFile, File

from src.client.s3_client import S3Client


@dataclass
class FileService:
    s3_client: S3Client

    async def handle_file_upload(self, file: UploadFile, user_id: int) -> str:
        """
        Service layer method to handle file upload logic.

        :param file: File to be uploaded.
        :param user_id: User ID for identifying the uploader.
        :return: URL of the uploaded file.
        """
        return self.s3_client.upload_file(file, user_id)

    @staticmethod
    def get_public_bucket() -> set[str]:
        return {"public-file"}

    def get_file_from_bucket(self, bucket: str, file_key: str) -> File:
        return self.s3_client.get_file(bucket, file_key)