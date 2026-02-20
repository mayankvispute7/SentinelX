# app/services/feature_engineering.py
import pandas as pd

def process_transaction(data: dict) -> pd.DataFrame:
    # 1. Convert dictionary to DataFrame
    df = pd.DataFrame([data])
    
    # 2. Force the exact column order the XGBoost model expects
    expected_columns = [
        'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 
        'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 
        'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 
        'V28', 'Amount'
    ]
    
    # Reorder the dataframe columns
    df = df[expected_columns]
    
    return df