from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import dotenv_values

config = dotenv_values("webserver/.env")
MONGO_USERNAME = config["MONGO_USERNAME"]
MONGO_PASSWORD = config["MONGO_PASSWORD"]
MONGO_DATABASE = config["MONGO_DATABASE"]

MONGODB_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:6000/{MONGO_DATABASE}?authSource=admin"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGO_DATABASE]
