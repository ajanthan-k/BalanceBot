from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from connection_manager import rover_manager, frontend_manager

router = APIRouter()


@router.websocket("/ws/rover")
async def websocket_rover(websocket: WebSocket):
    await rover_manager.connect(websocket)
    await frontend_manager.send_log("Rover connected")
    await frontend_manager.send_data({"type": "connection_status", "connected": True})
    try:
        while True:
            rover_data = await websocket.receive_json()

            if rover_data["type"] == "Sensors":
                sensor_data = rover_data["Sense_Array"]

                # Ultrasonic array- L R F
                dr_pos = [sensor_data[0], sensor_data[1]]
                dr_angle = sensor_data[2]
                left_us, right_us, front_us = (
                    sensor_data[3],
                    sensor_data[4],
                    sensor_data[5],
                )
                print("Sensor Data: ", dr_pos, dr_angle, front_us, left_us, right_us)

                # TODO: determine movement based on sensor data
                # loop = asyncio.get_event_loop()
                # command = await loop.run_in_executor(None, manager.default_navigate, dr_pos, dr_angle, front_us, left_us, right_us)

                # if command == "j":
                #     print("Junction detected")
                #     # tell beacons to turn on
                #     await frontend_manager.send_log("Junction detected - scanning started")
                #     global beacon_on
                #     beacon_on = True
                #     await rover_manager.send_data({"type": "scan"})

                # elif command == "None":
                #     print("No command")
                # either send forwards, or just handle receiving nothing on ESP as just continuing forwards

            elif rover_data["type"] == "Beacons":
                beacon_data = rover_data["Beacon_Array"]
                print("Beacon data received: ", beacon_data)
                ## TODO: determine action based on beacon scan

                # red_angle = beacon_data[0]
                # yellow_angle = beacon_data[1]
                # blue_angle = beacon_data[2]

                # angle_array = rover_data["Sample_Angle_Array"]
                # left_scan_array = rover_data["Left_Scan_Array"]
                # right_scan_array = rover_data["Right_Scan_Array"]

                # command = manager.junction_navigate(alpha, beta, gamma, readings)

            elif rover_data["type"] == "log":
                await frontend_manager.send_log(rover_data["message"])

    except WebSocketDisconnect:
        rover_manager.disconnect()
        await frontend_manager.send_log("Rover disconnected")
        await frontend_manager.send_data(
            {"type": "connection_status", "connected": False}
        )
