from email.message import EmailMessage
from typing import Any

import pytest

from app.infrastructure.email import EmailDelivery, SMTPEmailSender


class FakeSMTP:
    sent: EmailMessage | None = None

    def __init__(self, host: str, port: int, *, timeout: float) -> None:
        assert (host, port, timeout) == ('mailpit', 1025, 10.0)

    def __enter__(self) -> FakeSMTP:
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def send_message(self, message: EmailMessage) -> None:
        type(self).sent = message


@pytest.mark.asyncio
async def test_smtp_adapter_delivers_plain_text_without_header_injection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr('app.infrastructure.email.smtplib.SMTP', FakeSMTP)
    sender = SMTPEmailSender(host='mailpit', port=1025, sender='no-reply@example.test')

    await sender.send(
        EmailDelivery(
            recipient='person@example.test',
            subject='Convite seguro',
            text='Use o convite apenas uma vez.',
        )
    )

    assert FakeSMTP.sent is not None
    assert FakeSMTP.sent['To'] == 'person@example.test'
    assert FakeSMTP.sent['From'] == 'no-reply@example.test'
    assert FakeSMTP.sent.get_content().strip() == 'Use o convite apenas uma vez.'


@pytest.mark.asyncio
async def test_smtp_adapter_rejects_newlines_in_headers() -> None:
    sender = SMTPEmailSender(host='mailpit', port=1025, sender='no-reply@example.test')
    with pytest.raises(ValueError, match='header'):
        await sender.send(
            EmailDelivery(
                recipient='person@example.test\nBcc: attacker@example.test',
                subject='Convite',
                text='Conteúdo',
            )
        )
