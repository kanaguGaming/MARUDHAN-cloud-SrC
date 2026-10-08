from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db.database import db_config
from core.arivu_engine import process_telemetry_stub

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class TelemetryPayload(BaseModel):
    device_id: str
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    soil_moisture_percent: Optional[float] = None
    wind_speed_ms: Optional[float] = None

@router.post("/api/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    data_dict = payload.model_dump()
    
    # Process through ARIVU
    processed_data = process_telemetry_stub(data_dict)
    
    # Save to Digital Twin (MongoDB)
    if db_config.db is not None:
        collection = db_config.db["telemetry"]
        await collection.insert_one(processed_data)
        
    return {"status": "success", "message": "Telemetry ingested and processed by ARIVU"}

@router.get("/api/digital_twin/latest")
async def get_latest_twin_data():
    if db_config.db is not None:
        collection = db_config.db["telemetry"]
        # Get latest 10 records, exclude MongoDB ObjectID which isn't serializable by default
        cursor = collection.find({}, {"_id": 0}).sort("_id", -1).limit(10)
        data = await cursor.to_list(length=10)
        return {"data": data}
    return {"data": []}

@router.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
