import asyncio
import smtplib
import ssl
import time
import mimetypes
from email.message import EmailMessage
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, field_validator
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class MailAttachment(BaseModel):
    filename: str
    content: bytes
    mime_type: Optional[str] = None


class MailMessage(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    html: bool = False
    attachments: List[MailAttachment] = Field(default_factory=list)


class MailConfig(BaseModel):
    host: str = "mail.asfes.ru"
    port: int = 465
    username: str
    password: str

    from_name: str = "ASFES Mailer"

    timeout: int = 10
    retry_count: int = 3
    retry_delay: float = 1.0
    rate_limit: float = 0.0 
    @field_validator("retry_count")
    def _retry_count_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("retry_count должен быть >= 1")
        if v > 10:
            raise ValueError("retry_count слишком большой (макс 10)")
        return v


class MailClient:
    """
    Асинхронный SMTP-клиент ASFESLIB через smtplib.SMTP_SSL.

    Причины реализации:
    - aiosmtplib несовместим с mail.asfes.ru (AUTH LOGIN → 535)
    - smtplib работает идеально, но синхронный
    - asyncio.to_thread позволяет использовать его асинхронно

    Важное:
    КАЖДОЕ письмо создаёт новое SSL соединение SMTP.
    Это гарантирует корректный AUTH LOGIN.
    """

    def __init__(self, cfg: MailConfig):
        self.cfg = cfg
        self._rate_lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def _rate_limit(self):
        if self.cfg.rate_limit > 0:
            async with self._rate_lock:
                await asyncio.sleep(self.cfg.rate_limit)

    def _build_email(self, msg: MailMessage) -> EmailMessage:
        email = EmailMessage()
        email["From"] = f"{self.cfg.from_name} <{self.cfg.username}>"
        email["To"] = ", ".join(msg.to)
        email["Subject"] = msg.subject

        if msg.html:
            email.set_content(msg.body, subtype="html")
        else:
            email.set_content(msg.body)

        for att in msg.attachments:
            mime = att.mime_type or mimetypes.guess_type(att.filename)[0] or "application/octet-stream"
            main_type, sub_type = mime.split("/", 1)
            email.add_attachment(att.content, maintype=main_type, subtype=sub_type, filename=att.filename)

        return email
    
    def _normalize_login(self, username: str, password: str):
        """
        smtplib.SMTP_SSL expects `str` credentials.
        They must be ASCII-compatible, but provided as Python str.

        Поэтому:
        - гарантируем str
        - НЕ конвертируем в bytes
        - доверяем smtplib.base64_encode
        """
        return str(username), str(password)


    async def send(self, msg: MailMessage, log: bool = False) -> bool:
        await self._rate_limit()

        email = self._build_email(msg)

        for attempt in range(1, self.cfg.retry_count + 1):
            try:

                def blocking():
                    context = ssl.create_default_context()

                    t0 = time.perf_counter()
                    smtp = smtplib.SMTP_SSL(
                        self.cfg.host,
                        self.cfg.port,
                        timeout=self.cfg.timeout,
                        context=context
                    )
                    try:
                        peer = smtp.sock.getpeername()
                        if log:
                            logger.info(f"SMTP: connected to {peer[0]}:{peer[1]} (host={self.cfg.host!r})")
                    except Exception as e:
                        logger.error(f"SMTP: cannot getpeername: {e!r}")
                    t1 = time.perf_counter()
                    if log:
                        logger.info(f"SMTP: connect OK за {t1 - t0:.3f} сек")

                    username, password = self._normalize_login(
                        self.cfg.username,
                        self.cfg.password
                    )

                    smtp.login(username, password)
                    t2 = time.perf_counter()
                    if log:
                        logger.info(f"SMTP: login OK за {t2 - t1:.3f} сек")

                    smtp.send_message(email)
                    t3 = time.perf_counter()
                    if log:
                        logger.info(f"SMTP: send_message OK за {t3 - t2:.3f} сек")

                    smtp.quit()
                    t4 = time.perf_counter()
                    if log:
                        logger.info(f"SMTP: quit OK за {t4 - t3:.3f} сек")
                        logger.info(f"SMTP: всего за {t4 - t0:.3f} сек")

                await asyncio.to_thread(blocking)
                if log:
                    logger.info(f"Email sent → {msg.to}")
                return True

            except Exception as e:
                logger.error(f"SMTP error on attempt {attempt}: {e}")

                if attempt < self.cfg.retry_count:
                    await asyncio.sleep(self.cfg.retry_delay)

        logger.error(f"Failed to send email after {self.cfg.retry_count} attempts")
        return False

    async def send_bulk(self, messages: List[MailMessage]) -> List[bool]:
        results = []
        for msg in messages:
            results.append(await self.send(msg))
        return results

async def send_mail(cfg: MailConfig, msg: MailMessage) -> bool:
    async with MailClient(cfg) as client:
        return await client.send(msg)
