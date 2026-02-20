# app/models/transaction.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from app.models.database import Base

class TransactionLog(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    action = Column(String, nullable=False)
    model_version = Column(String, nullable=False) # PHASE 1: Model Versioning
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))