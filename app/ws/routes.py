from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.manager import ws_manager

router = APIRouter()

@router.websocket("/ws/items")
async def websocket_items(websocket: WebSocket):
    await ws_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
