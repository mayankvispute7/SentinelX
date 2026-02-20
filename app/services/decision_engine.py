# app/services/decision_engine.py

def get_risk_assessment(probability: float) -> dict:
    if probability >= 0.80:
        return {"risk_level": "HIGH", "action": "BLOCK"}
    elif probability >= 0.50:
        return {"risk_level": "MEDIUM", "action": "REVIEW_REQUIRED"}
    else:
        return {"risk_level": "LOW", "action": "APPROVE"}