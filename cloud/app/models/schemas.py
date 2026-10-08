from pydantic import BaseModel
from typing import Optional

class TelemetryPayload(BaseModel):
    device_id: str
    timestamp: str
    soil_moisture: float
    temperature: float
    humidity: float
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None

class DroneImagePayload(BaseModel):
    drone_id: str
    timestamp: str
    image_url: str
    gps_lat: float
    gps_lon: float
