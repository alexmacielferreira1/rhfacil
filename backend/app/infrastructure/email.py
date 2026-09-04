import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol


@dataclass(frozen=True)
class EmailDelivery:
    recipient: str
    subject: str
    text: str


class EmailSender(Protocol):
    async def send(self, delivery: EmailDelivery) -> None: ...


class SMTPEmailSender:
    def __init__(self, *, host: str, port: int, sender: str) -> None:
        self._host = host
        self._port = port
        self._sender = sender

    async def send(self, delivery: EmailDelivery) -> None:
        self._validate_header(delivery.recipient)
        self._validate_header(delivery.subject)
        self._validate_header(self._sender)
        message = EmailMessage()
        message['To'] = delivery.recipient
        message['From'] = self._sender
        message['Subject'] = delivery.subject
        message.set_content(delivery.text)
        await asyncio.to_thread(self._send_message, message)

    @staticmethod
    def _validate_header(value: str) -> None:
        if '\r' in value or '\n' in value:
            raise ValueError('Email header contains a forbidden newline.')

    def _send_message(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=10.0) as smtp:
            smtp.send_message(message)
