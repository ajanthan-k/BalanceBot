from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/ping")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "Ping":
            await websocket.send_text("Pong")
