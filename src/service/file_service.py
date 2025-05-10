from dataclasses import dataclass
from datetime import timedelta
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

    def get_file_from_bucket(
        self,
        bucket_name: str,
        file_key: str,
        offset: int | None = None,
        length: int | None = None,
    ):
        return self.s3_client.get_file(bucket_name, file_key, offset, length)

    async def delete_file_from_s3(self, user_id: str, filename: str) -> None:
        """
        Delete a file from S3
        """
        file_key = f"{user_id}/{filename}"
        self.s3_client.delete_file(file_key)

    @staticmethod
    def format_timestamp(seconds: float, use_comma: bool = True) -> str:
        """
        Переводит время в секундах (float) в строку формата
        SRT: HH:MM:SS,mmm
        VTT: HH:MM:SS.mmm
        """
        total_ms = int(round(seconds * 1000))
        td = timedelta(milliseconds=total_ms)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        ms = total_ms % 1000
        sep = ',' if use_comma else '.'
        return f"{hours:02}:{minutes:02}:{secs:02}{sep}{ms:03}"

    @staticmethod
    def json_to_plain_text(data: dict) -> str:
        """
        Собирает весь текст из сегментов в одну строку.
        """
        return " ".join(seg["text"].strip() for seg in data.get("segments", []))

    def json_to_srt(self, data: dict) -> str:
        """
        Генерирует контент для SRT-файла.
        """
        lines = []
        for idx, seg in enumerate(data.get("segments", []), start=1):
            start_ts = self.format_timestamp(seg["start"], use_comma=True)
            end_ts = self.format_timestamp(seg["end"], use_comma=True)
            lines.append(str(idx))
            lines.append(f"{start_ts} --> {end_ts}")
            lines.append(seg["text"].strip())
            lines.append("")  # пустая строка-разделитель
        return "\n".join(lines)

    def json_to_vtt(self, data: dict) -> str:
        """
        Генерирует контент для VTT (WebVTT)-файла.
        """
        lines = ["WEBVTT", ""]  # заголовок и пустая строка
        for seg in data.get("segments", []):
            start_ts = self.format_timestamp(seg["start"], use_comma=False)
            end_ts = self.format_timestamp(seg["end"], use_comma=False)
            lines.append(f"{start_ts} --> {end_ts}")
            lines.append(seg["text"].strip())
            lines.append("")  # разделитель
        return "\n".join(lines)
