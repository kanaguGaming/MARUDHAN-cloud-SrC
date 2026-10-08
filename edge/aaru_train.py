import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AARU_Trainer")

def train_aaru_model():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "../Dataset/ARIVU/irrigation_prediction.csv")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}")
        return
        
    logger.info("Loading AARU Dataset...")
    df = pd.read_csv(dataset_path)
    
    # Extract telemetry features
    features = ['Soil_Moisture', 'Temperature_C', 'Humidity']
    target = 'Irrigation_Need'
    
    # Drop rows with missing values in these columns
    df = df.dropna(subset=features + [target])
    
    X = df[features]
    
    # Encode Target (Low, Medium, High)
    le = LabelEncoder()
    y = le.fit_transform(df[target])
    
    logger.info("Training Irrigation Prediction Model (Random Forest)...")
    rf_irrigation = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    rf_irrigation.fit(X, y)
    
    model_path = os.path.join(model_dir, "aaru_irrigation_model.pkl")
    encoder_path = os.path.join(model_dir, "aaru_irrigation_encoder.pkl")
    
    joblib.dump(rf_irrigation, model_path)
    joblib.dump(le, encoder_path)
    
    logger.info(f"AARU model and encoder saved to {model_dir}")

if __name__ == "__main__":
    train_aaru_model()
