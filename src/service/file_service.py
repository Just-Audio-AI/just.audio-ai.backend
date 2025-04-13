from dataclasses import dataclass
from typing import BinaryIO


from src.client.s3_client import S3Client


@dataclass
class FileService:
    s3_client: S3Client

    async def upload_file_to_s3(
        self, file_obj: BinaryIO, user_id: int, filename: str
    ) -> str:
        """
        Upload a file to S3 and return the file URL
        """
        file_key = f"{user_id}/{filename}"
        self.s3_client.upload_file(file_obj, file_key)
        return file_key

    def get_public_bucket(self) -> set:
        return {"public-file"}

    def get_file_from_bucket(self, bucket_name: str, file_key: str):
        return self.s3_client.get_file(bucket_name, file_key)

    async def delete_file_from_s3(self, user_id: str, filename: str) -> None:
        """
        Delete a file from S3
        """
        file_key = f"{user_id}/{filename}"
        self.s3_client.delete_file(file_key)
