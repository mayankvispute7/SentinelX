# app/config.py
import os

# PHASE 1: Model Versioning
MODEL_VERSION = "1.0.0"
MODEL_PATH = os.path.join("ml_pipeline", "model_v1.pkl")

# PHASE 3: Basic Security Layer
SENTINELX_API_KEY = os.getenv("SENTINELX_API_KEY", "prod-super-secret-key-999")