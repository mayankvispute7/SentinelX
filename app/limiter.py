# app/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# PHASE 5: Rate Limiting
limiter = Limiter(key_func=get_remote_address)