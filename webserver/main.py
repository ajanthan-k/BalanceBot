import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

sys.path.append("./webserver")

from routers import frontend, rover, ping
from beacon_state import get_beacon_state, BeaconState
from database import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(frontend.router)
app.include_router(rover.router)
app.include_router(ping.router)

@app.get("/")
def index():
    return {"message": "Hello World!"}

@app.get("/logs")
def get_logs():
    return {"logs": frontend.frontend_manager.logs}

@app.post("/logs")
def reset_logs():
    print("Logs reset")
    frontend.frontend_manager.logs = []

@app.get("/mazehistory/id")
async def get_maze_ids():
    cursor = db["maze_history"].find({})
    ids = []
    async for doc in cursor:
        ids.append(str(doc["_id"]))
    return ids

@app.get("/connection_status")
def get_connection_status():
    is_connected = rover.rover_manager.active_connection is not None
    return {"connected": is_connected}

@app.get("/beacon")
def get_lights(beacon_state: BeaconState = Depends(get_beacon_state)):
    return beacon_state.get_beacon_on()
