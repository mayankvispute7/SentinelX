# app/services/fraud_model.py
import joblib
import pandas as pd
from app.config import MODEL_PATH # Importing the new V1 path

print(f"Loading ML Model into memory from: {MODEL_PATH}...")
model = joblib.load(MODEL_PATH)

def predict_fraud(features_df: pd.DataFrame) -> float:
    # Get the probability of the positive class (Fraud)
    probability = model.predict_proba(features_df)[0][1]
    return float(probability)