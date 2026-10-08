import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ARIVU_Trainer")

def train_arivu_models():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "../../Dataset/ARIVU/Smart_Farming_Crop_Yield_2024.csv")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}")
        return
        
    logger.info("Loading ARIVU Dataset...")
    df = pd.read_csv(dataset_path)
    
    # We only use features that the ESP32 telemetry provides
    features = ['soil_moisture_%', 'temperature_C', 'humidity_%']
    
    # Target 1: Yield Prediction (Regression)
    target_yield = 'yield_kg_per_hectare'
    X = df[features]
    y_yield = df[target_yield]
    
    logger.info("Training Yield Prediction Model (Random Forest)...")
    rf_yield = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_yield.fit(X, y_yield)
    yield_model_path = os.path.join(model_dir, "arivu_yield_model.pkl")
    joblib.dump(rf_yield, yield_model_path)
    logger.info(f"Yield model saved to {yield_model_path}")
    
    # Target 2: Crop Disease Status (Classification)
    target_disease = 'crop_disease_status'
    le = LabelEncoder()
    y_disease = le.fit_transform(df[target_disease].fillna('None'))
    
    logger.info("Training Disease Prediction Model (Random Forest)...")
    rf_disease = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_disease.fit(X, y_disease)
    
    disease_model_path = os.path.join(model_dir, "arivu_disease_model.pkl")
    encoder_path = os.path.join(model_dir, "arivu_disease_encoder.pkl")
    
    joblib.dump(rf_disease, disease_model_path)
    joblib.dump(le, encoder_path)
    logger.info(f"Disease model and encoder saved to {model_dir}")

if __name__ == "__main__":
    train_arivu_models()
