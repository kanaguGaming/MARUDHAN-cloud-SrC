from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "marudhan_twin"

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_config = Database()

async def connect_to_mongo():
    db_config.client = AsyncIOMotorClient(MONGO_URL)
    db_config.db = db_config.client[DB_NAME]
    print("Connected to MongoDB (Digital Twin)")

async def close_mongo_connection():
    if db_config.client:
        db_config.client.close()
        print("Closed MongoDB connection")
