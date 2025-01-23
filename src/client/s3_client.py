from fastapi import UploadFile, HTTPException
from minio import Minio
import uuid

class S3Client:
    def __init__(self, bucket_name: str, access_key: str, secret_key: str, s3_url: str, service_url: str):
        self.bucket_name = bucket_name
        self.s3 = Minio(
            endpoint=s3_url,
            secret_key=secret_key,
            access_key=access_key,
            secure=False
        )
        self.service_url = service_url

    def upload_file(self, file: UploadFile, user_id: int):
        """
        Upload a file to the S3 bucket.

        :param file: File to be uploaded.
        :param user_id: User ID for creating a unique file key.
        :return: URL of the uploaded file.
        """
        if not self.s3.bucket_exists(self.bucket_name):
            self.s3.make_bucket(bucket_name=self.bucket_name)
        try:
            # Generate a unique key for the file
            file_key = f"{user_id}/{uuid.uuid4()}-{file.filename}"

            # Upload the file to the S3 bucket
            self.s3.put_object(bucket_name=self.bucket_name, data=file.file, object_name=file_key, length=-1, part_size=10*1024*1024)

            # Return the public URL of the uploaded file
            return f"{self.service_url}/file/download/{self.bucket_name}/{file_key}"

        except Exception:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {file.filename}")

    def get_file(self, bucket: str, key: str):
        return self.s3.get_object(bucket_name=bucket, object_name=key)