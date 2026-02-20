# app/api/routes.py
import uuid
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import get_db
from app.models.transaction import TransactionLog
from app.schemas.transaction_schema import TransactionIn
from app.config import MODEL_VERSION
from app.api.security import verify_api_key
from app.limiter import limiter

from app.services.feature_engineering import process_transaction
from app.services.fraud_model import predict_fraud
from app.services.decision_engine import get_risk_assessment

router = APIRouter()

# PHASE 4: Lightweight In-Memory Drift State
drift_stats = {"total_reqs": 0, "sum_amount": 0.0, "sum_time": 0.0}
BASELINE_AVG_AMOUNT = 88.0 

@router.post("/predict")
@limiter.limit("50/minute") # PHASE 5: Rate Limiting
async def predict_transaction(
    request: Request, 
    transaction: TransactionIn, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key) # PHASE 3: Security
):
    request_id = str(uuid.uuid4())
    logger = logging.getLogger("SentinelX")
    logger = logging.LoggerAdapter(logger, {"request_id": request_id})
    
    logger.info(f"Received transaction for Amount: {transaction.Amount}")

    data_dict = transaction.model_dump()
    features_df = process_transaction(data_dict) 
    fraud_prob = predict_fraud(features_df)      
    decision = get_risk_assessment(fraud_prob)   
    
    db_transaction = TransactionLog(
        amount=transaction.Amount,
        fraud_probability=float(fraud_prob),
        risk_level=decision["risk_level"],
        action=decision["action"],
        model_version=MODEL_VERSION # PHASE 1
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    drift_stats["total_reqs"] += 1
    drift_stats["sum_amount"] += transaction.Amount
    drift_stats["sum_time"] += transaction.Time

    logger.info(f"Prediction complete. Action: {decision['action']}")
    
    return {
        "transaction_id": db_transaction.id,
        "fraud_probability": round(fraud_prob, 4),
        "risk_level": decision["risk_level"],
        "action": decision["action"],
        "model_version": MODEL_VERSION
    }

@router.get("/metrics")
async def get_system_metrics(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    total_transactions = db.query(TransactionLog).count()
    if total_transactions == 0:
        return {"message": "No transactions processed yet."}
        
    fraud_count = db.query(TransactionLog).filter(
        TransactionLog.risk_level.in_(["HIGH", "MEDIUM"])
    ).count()
    fraud_rate = round((fraud_count / total_transactions) * 100, 2)
    avg_score = db.query(func.avg(TransactionLog.fraud_probability)).scalar()
    
    return {
        "total_transactions_processed": total_transactions,
        "total_fraud_flags": fraud_count,
        "current_fraud_rate_percentage": fraud_rate,
        "average_system_risk_score": round(avg_score, 4)
    }

@router.get("/drift-metrics")
async def get_drift_metrics(api_key: str = Depends(verify_api_key)):
    if drift_stats["total_reqs"] == 0:
        return {"message": "No data to analyze yet."}
    
    current_avg_amount = drift_stats["sum_amount"] / drift_stats["total_reqs"]
    deviation = abs(current_avg_amount - BASELINE_AVG_AMOUNT)
    
    warning = "CRITICAL DRIFT DETECTED" if deviation > 50.0 else "NORMAL"

    return {
        "baseline_avg_amount": BASELINE_AVG_AMOUNT,
        "current_avg_amount": round(current_avg_amount, 2),
        "deviation": round(deviation, 2),
        "status": warning
    }