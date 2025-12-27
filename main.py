from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.ws.routes import router as ws_router
from app.db.database import init_db
from app.nats.client import nats_client
from app.tasks.background_task import background_task
from app.api.items import router as items_router
from app.api.tasks import router as tasks_router
from app.ws.manager import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    await nats_client.connect()
    
    async def handle_nats_message(data: dict):
        print(f"Обработка сообщения из NATS: {data}")

        await ws_manager.broadcast({
            "type": "nats_event",
            "payload": data
        })
    
    await nats_client.subscribe("items.updates", handle_nats_message)
    
    task = asyncio.create_task(background_task.start_periodic())
    background_task.task = task

    print("API документация: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/ws/items")
    
    yield
    
    await background_task.stop()
    await nats_client.disconnect()
    print("Приложение остановлено")

app = FastAPI(
    title="API",
    description="Асинхронный Backend",
    lifespan=lifespan
)

app.include_router(items_router)
app.include_router(ws_router, tags=["WebSocket"])
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {
        "message": "Currency Rates API",
        "docs": "/docs",
        "websocket": "/ws/items"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)