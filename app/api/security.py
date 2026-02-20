# app/api/security.py
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import SENTINELX_API_KEY

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != SENTINELX_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API Key"
        )
    return api_key