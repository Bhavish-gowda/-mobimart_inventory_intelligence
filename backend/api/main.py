"""
Main FastAPI Application Entry Point for MobiMart Inventory Intelligence System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.api.config import API_TITLE, API_VERSION, API_DESCRIPTION, API_PREFIX, CORS_ORIGINS
from backend.api.errors import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from backend.api.routers import (
    health,
    stores,
    products,
    inventory,
    forecast,
    allocation,
    eol,
    simulation,
)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include Routers under /api/v1
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(stores.router, prefix=API_PREFIX)
app.include_router(products.router, prefix=API_PREFIX)
app.include_router(inventory.router, prefix=API_PREFIX)
app.include_router(forecast.router, prefix=API_PREFIX)
app.include_router(allocation.router, prefix=API_PREFIX)
app.include_router(eol.router, prefix=API_PREFIX)
app.include_router(simulation.router, prefix=API_PREFIX)

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Welcome to MobiMart Inventory Intelligence API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
