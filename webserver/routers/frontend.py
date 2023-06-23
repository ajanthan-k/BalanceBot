import sys
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from connection_manager import frontend_manager, rover_manager
from webserver.beacon_state import get_beacon_state, BeaconState
from database import db
import asyncio

sys.path.append("./maze")

from maze_manager import MazeManager
from maze_sim import MazeSim

router = APIRouter()


@router.websocket("/ws/frontend")
async def websocket_frontend(websocket: WebSocket):
    await frontend_manager.connect(websocket)
    await frontend_manager.send_log("Frontend connected")
    try:
        while True:
            frontend_data = await websocket.receive_json()

            # Entry point into algorithm - initialise maze manager
            if frontend_data["type"] == "start":
                print("Start request from front end received")
            elif frontend_data["type"] == "stop":
                print("Stop request from front end received")
            elif frontend_data["type"] == "maze_id":
                # If message is a selected ID from dropdown
                selected_id = frontend_data["maze_id"]
                maze_data = await db["maze_history"].find_one({"_id": selected_id})

                print("Received maze data to send")
                # Send maze data back to frontend
                await websocket.send_json(
                    {
                        "type": "maze",
                        "start": maze_data["start"],
                        "end": maze_data["end"],
                        "edges": maze_data["edges"],
                        "path": maze_data["path"],
                    }
                )
            elif frontend_data["type"] == "message":
                await handle_manual_message(frontend_data["message"], websocket)

    except WebSocketDisconnect:
        print("Frontend disconnected")


async def handle_manual_message(
    message: str,
    websocket: WebSocket,
    beacon_state: BeaconState = Depends(get_beacon_state),
):
    print("Manual:", message)
    message_parts = message.split()
    command = message_parts[0]

    if command == "turn":
        await rover_manager.send_data(
            {"type": "movement", "command": command, "value": message_parts[1]}
        )
    elif command == "scan":
        await rover_manager.send_data({"type": "scan"})
    elif command == "beacon":
        beacon_state.set_beacon_on(bool(int(message_parts[1])))
    elif command == "sim":
        print("Maze no: ", message_parts[1])
        cycle_step = 5
        sim = MazeSim(int(message_parts[1]), bool(message_parts[2]), cycle_step)
        asyncio.create_task(update_simulation(websocket, sim))
    else:
        await rover_manager.send_data({"type": "movement", "command": message})
        await frontend_manager.send_log("Manual: " + message)


async def update_simulation(websocket: WebSocket, sim: MazeSim):
    await frontend_manager.send_log("Simulation started")
    while sim.update():
        edges = sim.manager.get_edges()
        path = sim.manager.get_path()
        robot_pos = sim.manager.get_pos()
        robot_angle = sim.manager.get_angle()

        await websocket.send_json(
            {
                "type": "maze",
                "edges": edges,
                "path": path,
                "rover": {"pos": robot_pos, "angle": robot_angle},
            }
        )

        await asyncio.sleep(0.1)

    await frontend_manager.send_log("Simulation complete")
