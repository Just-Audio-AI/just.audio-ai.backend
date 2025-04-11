from dataclasses import dataclass
import re

from fastapi import File, UploadFile

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
        clean_filename = self.clean_filename(file.filename)
        file.filename = clean_filename
        return self.s3_client.upload_file(file, user_id)

    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename from invalid URL characters.

        :param filename: Original filename
        :return: Cleaned filename
        """
        # Replace spaces and special characters
        clean_name = re.sub(r"[^\w\-_.]", "_", filename)
        # Remove multiple consecutive underscores
        clean_name = re.sub(r"_+", "_", clean_name)
        # Remove leading/trailing underscores
        clean_name = clean_name.strip("_")
        return clean_name

    @staticmethod
    def get_public_bucket() -> set[str]:
        return {"public-file"}

    def get_file_from_bucket(self, bucket: str, file_key: str) -> File:
        return self.s3_client.get_file(bucket, file_key)
