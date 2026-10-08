import os
import joblib
import pandas as pd
import logging
import numpy as np

logger = logging.getLogger("KANRU_Engine")

base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "models")

# Load models once at startup
try:
    health_model = joblib.load(os.path.join(model_dir, "kanru_health_model.pkl"))
    breed_encoder = joblib.load(os.path.join(model_dir, "kanru_breed_encoder.pkl"))
    logger.info("KANRU models loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load KANRU models: {e}")
    health_model, breed_encoder = None, None

HEALTH_CLASSES = {
    0: "Normal / Healthy",
    1: "Elevated Temperature / Fever",
    2: "Heat Stress",
    3: "Hypoxia / Respiratory Distress"
}

def process_livestock_telemetry(payload: dict) -> dict:
    """
    KANRU Engine: Predicts livestock health status and anomalies using trained models.
    """
    animal_id = payload.get("animal_id", "UNKNOWN")
    
    analysis = {
        "animal_id": animal_id,
        "health_status_class": -1,
        "health_status_label": "Unknown",
        "anomaly_confidence_score": 0.0,
        "deviation_index": 0.0,
        "ai_recommendation": "Unable to assess"
    }

    if health_model and breed_encoder:
        try:
            # Extract features matching the model training
            # Fallback to sensible defaults for unprovided features
            body_temp = payload.get("body_temperature", 38.5)
            heart_rate = payload.get("heart_rate", 60.0)
            spo2 = payload.get("spo2_level", 98.0)
            amb_temp = payload.get("ambient_temperature", 25.0)
            rel_humidity = payload.get("relative_humidity", 50.0)
            
            # THI calculation if not provided
            thi = payload.get("thi")
            if thi is None:
                thi = (1.8 * amb_temp + 32) - (0.55 - 0.0055 * rel_humidity) * (1.8 * amb_temp - 26)
                
            age_months = payload.get("age_months", 36)
            weight_kg = payload.get("weight_kg", 400.0)
            lactation_status = int(payload.get("lactation_status", 1))
            
            # Simulated rolling parameters / pathivu database values if missing
            rolling_7d_temp = payload.get("rolling_7d_temp", body_temp)
            hr_delta = payload.get("hr_delta", 0.0)
            
            breed_str = payload.get("breed", "Local")
            try:
                breed_encoded = breed_encoder.transform([breed_str])[0]
            except ValueError:
                # Fallback to 0 if breed is unseen
                breed_encoded = 0

            # Construct DataFrame
            features = [
                'body_temperature', 'heart_rate', 'spo2_level', 
                'ambient_temperature', 'relative_humidity', 'thi', 
                'age_months', 'weight_kg', 'lactation_status', 
                'rolling_7d_temp', 'hr_delta', 'breed_encoded'
            ]
            
            input_df = pd.DataFrame([[
                body_temp, heart_rate, spo2, amb_temp, rel_humidity, thi,
                age_months, weight_kg, lactation_status, rolling_7d_temp, hr_delta, breed_encoded
            ]], columns=features)
            
            # Predict probabilities and class
            probs = health_model.predict_proba(input_df)[0]
            pred_class = int(np.argmax(probs))
            confidence = float(probs[pred_class])
            
            # Calculate Deviation Index (standard deviations from baseline mock)
            # Just a simplistic stand-in calculation. Normally we would use population/individual std dev.
            deviation_index = float(abs(body_temp - rolling_7d_temp) / 0.5) 
            
            analysis["health_status_class"] = pred_class
            analysis["health_status_label"] = HEALTH_CLASSES.get(pred_class, "Unknown")
            analysis["anomaly_confidence_score"] = round(confidence, 4)
            analysis["deviation_index"] = round(deviation_index, 2)
            
            if pred_class == 0:
                analysis["ai_recommendation"] = "Vitals conform to baseline. No action required."
            elif pred_class == 1:
                analysis["ai_recommendation"] = "Elevated temperature detected. Monitor closely for signs of infection or mastitis. Isolate if required."
            elif pred_class == 2:
                analysis["ai_recommendation"] = "Heat stress detected. Relocate to shade, improve ventilation, and provide water."
            elif pred_class == 3:
                analysis["ai_recommendation"] = "Hypoxia / Respiratory distress detected! Seek veterinary intervention immediately."
                
        except Exception as e:
            logger.error(f"KANRU Prediction error: {e}")

    payload["kanru_analysis"] = analysis
    return payload
