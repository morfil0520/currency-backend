import asyncio
from app.db.database import AsyncSessionLocal
from app.services.currency_service import CurrencyService
from config import settings
from app.nats.client import nats_client

class BackgroundTask:
    def __init__(self):
        self._running = False
        self.task: asyncio.Task | None = None

    async def run_once(self):
        async with AsyncSessionLocal() as session:
            rates = await CurrencyService.fetch_from_cbr()
            await CurrencyService.save_to_db(session, rates)

            print(f"[CBR] Обновлено курсов: {len(rates)}")

            await nats_client.publish(
                "items.updates",
                {
                    "event": "rates_updated",
                    "count": len(rates),
                }
            )

    async def start_periodic(self):
        if self._running:
            return

        self._running = True

        while self._running:
            try:
                await self.run_once()
            except Exception as e:
                print("[CBR] Ошибка обновления:", e)

            await asyncio.sleep(settings.task_interval_seconds)

    async def stop(self):
        self._running = False

background_task = BackgroundTask()