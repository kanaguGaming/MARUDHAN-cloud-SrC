import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import GroupShuffleSplit
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KANRU_Trainer")

def synthesize_kanru_features(df):
    """
    Synthesize features needed for KANRU model from Infection_Risk_Dataset.
    The raw dataset has limited columns, so we synthesize the exact ones described in architecture.
    """
    np.random.seed(42)
    
    # 1. Animal ID & Time
    num_animals = 500
    df['animal_id'] = np.random.randint(1, num_animals + 1, df.shape[0])
    df = df.sort_values(by=['animal_id'])
    
    # Map directly available features
    df['body_temperature'] = df['Body_Temperature']
    df['ambient_temperature'] = df['Ambient_Temperature']
    df['relative_humidity'] = df['Relative_Humidity']
    df['breed'] = df['Breed']
    df['age_months'] = df['Age'] * 12
    
    # Synthesize missing features
    df['weight_kg'] = np.random.normal(400, 50, len(df))
    df['lactation_status'] = (df['Reproductive_Status'] == 'Lactating').astype(int)
    
    # Synthesize physiologicals (Heart rate and SpO2 based on Respiration_Rate and Activity_Level)
    df['heart_rate'] = df['Respiration_Rate'] * 2.5 + np.random.normal(0, 5, len(df))
    df['spo2_level'] = 98.0 - (df['Respiration_Rate'] - 20) * 0.1 + np.random.normal(0, 1, len(df))
    df['spo2_level'] = df['spo2_level'].clip(80, 100)
    
    # Contextual features
    # THI = (1.8 * T + 32) - (0.55 - 0.0055 * RH) * (1.8 * T - 26)
    T = df['ambient_temperature']
    RH = df['relative_humidity']
    df['thi'] = (1.8 * T + 32) - (0.55 - 0.0055 * RH) * (1.8 * T - 26)
    
    # Historical Deltas (Rolling 7-record average for simplicity)
    df['rolling_7d_temp'] = df.groupby('animal_id')['body_temperature'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df['hr_delta'] = df.groupby('animal_id')['heart_rate'].diff().fillna(0)
    
    # Target Label (Health Status Classification)
    # Class 0: Normal, Class 1: Fever, Class 2: Heat Stress, Class 3: Hypoxia
    conditions = [
        (df['spo2_level'] < 90) & (df['heart_rate'] > 100), # Class 3 - Hypoxia
        (df['thi'] > 72) & (df['body_temperature'] > 39.5), # Class 2 - Heat Stress
        (df['body_temperature'] > 39.5) & (df['thi'] <= 72), # Class 1 - Fever
    ]
    choices = [3, 2, 1]
    df['target'] = np.select(conditions, choices, default=0)
    
    return df

def train_kanru_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "../../Dataset/KANRU/Infection_Risk_Dataset.csv")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}")
        return
        
    logger.info("Loading KANRU Dataset...")
    df = pd.read_csv(dataset_path)
    
    logger.info("Synthesizing required features...")
    df = synthesize_kanru_features(df)
    
    # Features required for training
    features = [
        'body_temperature', 'heart_rate', 'spo2_level', 
        'ambient_temperature', 'relative_humidity', 'thi', 
        'age_months', 'weight_kg', 'lactation_status', 
        'rolling_7d_temp', 'hr_delta'
    ]
    
    # We will categorical encode 'breed'
    le_breed = LabelEncoder()
    df['breed_encoded'] = le_breed.fit_transform(df['breed'].astype(str))
    features.append('breed_encoded')
    
    X = df[features]
    y = df['target']
    groups = df['animal_id']
    
    logger.info("Performing GroupShuffleSplit by animal_id...")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    logger.info("Training KANRU Multivariate Health Classifier (XGBoost)...")
    model = XGBClassifier(
        objective='multi:softprob',
        num_class=4,
        eval_metric='mlogloss',
        n_estimators=100,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    logger.info(f"Training Accuracy: {train_acc:.4f}")
    logger.info(f"Testing Accuracy: {test_acc:.4f}")
    
    model_path = os.path.join(model_dir, "kanru_health_model.pkl")
    encoder_path = os.path.join(model_dir, "kanru_breed_encoder.pkl")
    
    joblib.dump(model, model_path)
    joblib.dump(le_breed, encoder_path)
    
    logger.info(f"KANRU Model saved to {model_path}")

if __name__ == "__main__":
    train_kanru_models()
