import os
import joblib
import pandas as pd
import logging

logger = logging.getLogger("ARIVU_Engine")

base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "models")

# Load models once at startup
try:
    yield_model = joblib.load(os.path.join(model_dir, "arivu_yield_model.pkl"))
    disease_model = joblib.load(os.path.join(model_dir, "arivu_disease_model.pkl"))
    disease_encoder = joblib.load(os.path.join(model_dir, "arivu_disease_encoder.pkl"))
    logger.info("ARIVU models loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load ARIVU models: {e}")
    yield_model, disease_model, disease_encoder = None, None, None

def process_telemetry(payload: dict) -> dict:
    """
    ARIVU Engine: Predicts crop yield and disease status using trained models.
    """
    device_id = payload.get("device_id", "UNKNOWN")
    
    analysis = {
        "device_id": device_id,
        "crop_health_status": "Unknown",
        "predicted_yield_kg_per_ha": 0.0,
        "ai_recommendation": "Maintain operations"
    }

    if yield_model and disease_model and disease_encoder:
        try:
            # Extract features matching the model training
            moisture = payload.get("soil_moisture_percent", 0.0)
            temp = payload.get("temperature_c", 0.0)
            humidity = payload.get("humidity_percent", 0.0)
            
            # Predict Yield
            input_df = pd.DataFrame([[moisture, temp, humidity]], columns=['soil_moisture_%', 'temperature_C', 'humidity_%'])
            pred_yield = yield_model.predict(input_df)[0]
            
            # Predict Disease
            pred_disease_encoded = disease_model.predict(input_df)[0]
            pred_disease = disease_encoder.inverse_transform([pred_disease_encoded])[0]
            
            analysis["predicted_yield_kg_per_ha"] = round(pred_yield, 2)
            analysis["crop_health_status"] = pred_disease
            
            if pred_disease in ["Severe", "Moderate"]:
                analysis["ai_recommendation"] = "Immediate attention required. Recommend pesticide or agronomic review."
            else:
                analysis["ai_recommendation"] = "Conditions are optimal."
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")

    payload["arivu_analysis"] = analysis
    return payload

# Alias to avoid breaking existing imports in endpoints.py
process_telemetry_stub = process_telemetry
