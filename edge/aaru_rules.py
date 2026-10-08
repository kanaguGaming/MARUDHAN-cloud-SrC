import os
import joblib
import pandas as pd
import logging

logger = logging.getLogger("AARU_Rules")

WIND_SPEED_THRESHOLD = 15.0 # m/s (for drone safety)

base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "models")

try:
    irrigation_model = joblib.load(os.path.join(model_dir, "aaru_irrigation_model.pkl"))
    irrigation_encoder = joblib.load(os.path.join(model_dir, "aaru_irrigation_encoder.pkl"))
    logger.info("AARU ML models loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load AARU models: {e}")
    irrigation_model, irrigation_encoder = None, None

def evaluate_telemetry(payload: dict):
    """
    Evaluates autonomous rules based on trained ML models and local telemetry.
    """
    device_id = payload.get("device_id", "UNKNOWN")
    
    # 1. Irrigation Logic (MANN Node) using ML
    if irrigation_model and irrigation_encoder:
        if all(k in payload for k in ["soil_moisture_percent", "temperature_c", "humidity_percent"]):
            moisture = payload["soil_moisture_percent"]
            temp = payload["temperature_c"]
            humidity = payload["humidity_percent"]
            
            try:
                input_df = pd.DataFrame([[moisture, temp, humidity]], columns=['Soil_Moisture', 'Temperature_C', 'Humidity'])
                pred_encoded = irrigation_model.predict(input_df)[0]
                irrigation_need = irrigation_encoder.inverse_transform([pred_encoded])[0]
                
                if irrigation_need in ["High", "Medium"]:
                    logger.info(f"[AARU ACTUATION] Irrigation Need is {irrigation_need} for {device_id}. Triggering irrigation pump.")
                    # Here we would publish a command back to the device to actuate the pump
                else:
                    logger.debug(f"Irrigation Need is {irrigation_need} for {device_id}.")
            except Exception as e:
                logger.error(f"AARU prediction error: {e}")
    else:
        # Fallback logic if models fail to load
        if "soil_moisture_percent" in payload:
            if payload["soil_moisture_percent"] < 30.0:
                 logger.info(f"[AARU ACTUATION] Soil moisture low for {device_id}. Triggering irrigation pump (Fallback).")
                 
    # 2. Drone Deployment Safety Logic (WIN Node)
    if "wind_speed_ms" in payload:
        wind = payload["wind_speed_ms"]
        if wind > WIND_SPEED_THRESHOLD:
            logger.warning(f"[SAFETY] High wind speed detected ({wind} m/s). Drone deployment is RESTRICTED.")
        else:
            logger.info("[SAFETY] Weather optimal. Drone deployment is SAFE.")
