import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.settings import Settings

class MailClient:
    def __init__(self, settings: Settings):
        self.from_email = settings.from_email
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_password = settings.SMTP_PASSWORD

    async def send_code(self, code: int, to: str) -> None:
        msg = await self.__build_message(f"Fitra auth code {code}", f"Your code is {code}", to)
        await self.__send_message(msg)

    async def __build_message(self, subject: str, text: str, to: str) -> MIMEMultipart:
        msg = MIMEMultipart()

        msg["From"] = self.from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))
        return msg

    async def __send_message(self, msg: MIMEMultipart) -> None:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context)
        server.login(self.from_email, self.smtp_password)
        server.send_message(msg)
        server.quit()
