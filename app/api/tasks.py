from fastapi import APIRouter
from app.tasks.background_task import background_task

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/run")
async def run_task():
    await background_task.run_once()
    return {
        "status": "ok",
        "message": "Фоновая задача выполнена вручную"
    }
