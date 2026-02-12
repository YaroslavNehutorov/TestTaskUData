from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.websocket.manager import manager

ws_router = APIRouter()


@ws_router.websocket("/ws/lots")
async def websocket_all_lots(websocket: WebSocket):
    await manager.connect_global(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_global(websocket)


@ws_router.websocket("/ws/lots/{lot_id}")
async def websocket_lot(websocket: WebSocket, lot_id: int):
    await manager.connect(lot_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(lot_id, websocket)
