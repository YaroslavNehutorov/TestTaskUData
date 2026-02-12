from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)
        self.global_connections: list[WebSocket] = []

    async def connect(self, lot_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[lot_id].append(websocket)

    def disconnect(self, lot_id: int, websocket: WebSocket):
        if websocket in self.active_connections[lot_id]:
            self.active_connections[lot_id].remove(websocket)

    async def connect_global(self, websocket: WebSocket):
        await websocket.accept()
        self.global_connections.append(websocket)

    def disconnect_global(self, websocket: WebSocket):
        if websocket in self.global_connections:
            self.global_connections.remove(websocket)

    async def broadcast(self, lot_id: int, message: dict):
        for connection in self.active_connections[lot_id][:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(lot_id, connection)
        for connection in self.global_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect_global(connection)


manager = ConnectionManager()
