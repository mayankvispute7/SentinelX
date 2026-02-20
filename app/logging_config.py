# app/logging_config.py
import logging
import json
from datetime import datetime, timezone

# PHASE 2: Structured Logging System
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        return json.dumps(log_record)

def configure_logging():
    logger = logging.getLogger("SentinelX")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)