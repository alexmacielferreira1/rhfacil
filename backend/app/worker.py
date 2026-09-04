import asyncio
from time import monotonic

from app.core.config import get_settings
from app.core.database import create_engine
from app.infrastructure.email import SMTPEmailSender
from app.modules.jobs.email_processor import process_email_cycle
from app.modules.maintenance.retention import run_retention_cycle


async def run_worker() -> None:
    settings = get_settings()
    engine = create_engine(settings)
    sender = SMTPEmailSender(
        host=settings.smtp_host,
        port=settings.smtp_port,
        sender=settings.email_sender,
    )
    next_maintenance = 0.0
    try:
        while True:
            if monotonic() >= next_maintenance:
                await run_retention_cycle(engine, settings)
                next_maintenance = monotonic() + settings.maintenance_interval_seconds
            completed = await process_email_cycle(
                engine,
                sender=sender,
                secret=settings.auth_secret,
                public_app_url=settings.public_app_url,
            )
            if completed == 0:
                await asyncio.sleep(settings.worker_poll_seconds)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(run_worker())
