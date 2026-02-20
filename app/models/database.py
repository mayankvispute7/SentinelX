# app/models/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Fetch the URL from the environment (Docker), OR default to local (Your laptop)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:admin123@127.0.0.1:5432/sentinelx"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session in our API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()