"""
Configuration settings for MobiMart FastAPI Layer.
"""

import os
from typing import List

API_TITLE = "MobiMart Inventory Intelligence API"
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
API_DESCRIPTION = (
    "Enterprise-grade inventory intelligence REST API for MobiMart retail chain. "
    "Provides demand forecasting, constrained greedy allocation, EOL risk management, "
    "portfolio transfer resolution, and 52-week rolling simulation benchmarking."
)

# CORS configuration (Default: local React/Vite development origins)
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
if CORS_ORIGINS_ENV:
    CORS_ORIGINS: List[str] = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",") if origin.strip()]
else:
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
