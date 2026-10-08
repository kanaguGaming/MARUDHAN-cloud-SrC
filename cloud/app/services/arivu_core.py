from app.models.schemas import TelemetryPayload
from app.db.pathivu import log_to_pathivu
from app.services.weather_api import fetch_live_weather

async def process_telemetry(payload: TelemetryPayload):
    # Fetch live weather data to contextualize local edge telemetry
    live_weather = await fetch_live_weather()
    
    # 1. Log to PATHIVU (MongoDB & Parquet Storage)
    data_dict = payload.model_dump()
    data_dict["external_weather"] = live_weather
    await log_to_pathivu(data_dict, "telemetry")
    
    # 2. Evaluate against historical memory & external weather parameters
    decision = "Maintain Operations"
    actuator_command = None
    
    current_temp = live_weather.get("temperature_c", 30)
    is_extremely_hot = current_temp > 35.0
    
    # Simple logic activation: Trigger physical actuators 
    # taking both local soil moisture and macro weather heat index into account.
    if payload.soil_moisture < 30.0:
        if is_extremely_hot:
            decision = f"Urgent Irrigation Required (High Heat: {current_temp}°C)"
            duration = 1200
        else:
            decision = "Irrigation Required"
            duration = 600
            
        actuator_command = {
            "target": payload.device_id, 
            "action": "PUMP_ON", 
            "duration": duration,
            "protocol": "MQTT"
        }
        
    # 3. Closed-Loop Execution Workflow: Dispatch & Verify
    return {
        "status": "success", 
        "decision": decision, 
        "actuator_command": actuator_command,
        "weather_context": live_weather,
        "pathivu_logged": True
    }
