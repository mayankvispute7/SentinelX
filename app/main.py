# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.routes import router
from app.models.database import engine, Base
from app.logging_config import configure_logging
from app.limiter import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelX Real-Time Fraud Engine", version="1.0")

# Apply Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Initialize JSON Logs
configure_logging()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "SentinelX Enterprise API is online."}