from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import os
from datetime import datetime

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "PATHIVU"

class PathivuDatabase:
    client: AsyncIOMotorClient = None
    db = None

pathivu_db = PathivuDatabase()

async def connect_to_pathivu():
    pathivu_db.client = AsyncIOMotorClient(MONGO_URL)
    pathivu_db.db = pathivu_db.client[DB_NAME]
    print(f"Connected to PATHIVU MongoDB Server at {MONGO_URL}")

async def close_pathivu_connection():
    if pathivu_db.client:
        pathivu_db.client.close()
        print("Closed PATHIVU MongoDB connection")

async def log_to_pathivu(data: dict, collection_name: str):
    """Log validated telemetry into MongoDB PATHIVU database and backup to Parquet."""
    # 1. Log to MongoDB
    if pathivu_db.db is not None:
        collection = pathivu_db.db[collection_name]
        db_record = data.copy()
        db_record['created_at'] = datetime.utcnow().isoformat()
        await collection.insert_one(db_record)
    
    # 2. Log to Apache Parquet formats (as per Edge-Heavy architecture specs)
    df = pd.DataFrame([data])
    dir_path = f"dataset/PATHIVU/{collection_name}"
    os.makedirs(dir_path, exist_ok=True)
    file_path = f"{dir_path}/data.parquet"
    
    try:
        import pyarrow
        if os.path.exists(file_path):
            existing_df = pd.read_parquet(file_path)
            df = pd.concat([existing_df, df])
        df.to_parquet(file_path, engine="pyarrow")
    except ImportError:
        # Fallback to CSV if pyarrow is missing
        csv_path = file_path.replace('.parquet', '.csv')
        df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
        
    return file_path
