from fastapi import APIRouter
from app.models.schemas import TelemetryPayload, DroneImagePayload
from app.services.arivu_core import process_telemetry
from app.services.nalam_vision import analyze_drone_image
from app.services.kural_unmai import get_kural_response
from app.services.aadi_twin import get_digital_twin_state
from app.services.varavu_valam import calculate_roi, calculate_efficiency

api_router = APIRouter()

@api_router.post("/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    return await process_telemetry(payload)

@api_router.post("/vision/analyze")
async def ingest_drone_imagery(payload: DroneImagePayload):
    return await analyze_drone_image(payload)

@api_router.post("/chat/kural")
async def chat_kural(query: str):
    return await get_kural_response(query)

@api_router.get("/twin/aadi")
async def digital_twin():
    return await get_digital_twin_state()

@api_router.get("/finance/varavu")
async def get_varavu():
    return await calculate_roi()

@api_router.get("/resources/valam")
async def get_valam():
    return await calculate_efficiency()
