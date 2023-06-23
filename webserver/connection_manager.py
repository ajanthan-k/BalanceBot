from fastapi import WebSocket
from datetime import datetime
from zoneinfo import ZoneInfo

class ConnectionManager:
    def __init__(self):
        self.active_connection = None
        self.logs = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection = websocket

    def disconnect(self):
        self.active_connection = None

    async def send_data(self, data: dict):
        if self.active_connection:
            await self.active_connection.send_json(data)

    async def send_log(self, message: str):
        t = datetime.now(ZoneInfo("Europe/London"))
        cur_time = t.strftime("%H:%M:%S")
        if self.active_connection:
            log = {"type": "log", "time": cur_time, "message": message}
            self.logs.append(log)
            await self.active_connection.send_json(log)

frontend_manager = ConnectionManager()
rover_manager = ConnectionManager()
