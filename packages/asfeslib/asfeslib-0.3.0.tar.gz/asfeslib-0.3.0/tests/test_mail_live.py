import os
import time
import pytest
from asfeslib.net.mail import MailClient, MailConfig, MailMessage

SMTP_KEY_ENV = "ASFESLIB_SMTP_PASSWORD"
SMTP_USER_ENV = "ASFESLIB_SMTP_USER"

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_live_mail_send():
    start = time.perf_counter()

    user = os.getenv(SMTP_USER_ENV)
    password = os.getenv(SMTP_KEY_ENV)

    if not user or not password:
        pytest.skip("Нет ASFESLIB_SMTP_USER / ASFESLIB_SMTP_PASSWORD")

    cfg = MailConfig(
        username=user,
        password=password,
        port=465,
        timeout=5,
        retry_count=1,
        rate_limit=0.0,
    )

    msg = MailMessage(
        to=["admin@asfes.ru"],
        subject="ASFESLIB Live SMTP Test",
        body="SMTP test is successful!",
        html=False,
    )

    async with MailClient(cfg) as mail:
        ok = await mail.send(msg, log=True)

    elapsed = time.perf_counter() - start
    print(f"[test_live_mail_send] Успешно за {elapsed:.3f} сек")

    assert ok is True
