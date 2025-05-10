from typing import BinaryIO

from fastapi import File, HTTPException
from minio import Minio, S3Error


class S3Client:
    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        s3_url: str,
        service_url: str,
    ):
        self.bucket_name = bucket_name
        self.s3 = Minio(
            endpoint=s3_url, secret_key=secret_key, access_key=access_key, secure=False
        )
        self.service_url = service_url

    def upload_file(self, file: BinaryIO, file_key: str) -> str:
        """
        Upload a file to the S3 bucket.

        :param file: File to be uploaded.
        :param user_id: User ID for creating a unique file key.
        :return: URL of the uploaded file.
        """
        if not self.s3.bucket_exists(self.bucket_name):
            self.s3.make_bucket(bucket_name=self.bucket_name)
        try:
            # Upload the file to the S3 bucket
            self.s3.put_object(
                bucket_name=self.bucket_name,
                data=file,
                object_name=file_key,
                length=-1,
                part_size=10 * 1024 * 1024,
            )

            # Return the file key (which is now clean)
            return file_key

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {file_key}. Error: {str(e)}",
            )

    def get_object_size(self, bucket_name: str, object_name: str) -> int:
        try:
            info = self.s3.stat_object(bucket_name, object_name)
            return info.size
        except S3Error as err:
            # обработка ошибки
            raise RuntimeError(f"Не удалось получить размер объекта: {err}")

    def get_file(
        self,
        bucket: str,
        file_key: str,
        offset: int | None = None,
        length: int | None = None,
    ) -> File:
        return self.s3.get_object(
            bucket_name=bucket, object_name=file_key, length=length, offset=offset
        )

    def delete_file(self, file_key: str) -> None:
        """
        Delete a file from the S3 bucket.

        :param file_key: Key of the file to delete.
        """
        try:
            self.s3.remove_object(bucket_name=self.bucket_name, object_name=file_key)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {file_key}. Error: {str(e)}",
            )
