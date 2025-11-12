# vintrick-backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import all routers
from app.api.routes.harvestloads import router as harvestloads_router
from app.api.routes.blends import router as blends_router
from app.api.routes.trans_sum import router as trans_sum_router
from app.api.routes.vintrace_pull import router as vintrace_pull_router
from app.api.routes.meta import router as meta_router
from app.api.routes.trans_sum_sync import router as trans_sum_sync_router
from app.api.routes.shipments import router as shipments_router  # <--- NEW ROUTE
from app.api.routes.harvestload_agcode import router as harvestload_agcode_router

# Import improved error handlers from utils
from tools.utils.error_utils import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

app = FastAPI(debug=True)

# Add CORS middleware - for dev, '*' is OK, but restrict for prod!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)


app.include_router(harvestload_agcode_router, prefix="/api", tags=["harvestload_agcode"])

# Register all routers (just as before)

app.include_router(harvestloads_router,     prefix="/api",      tags=["harvestloads"])
app.include_router(blends_router,           prefix="/api",      tags=["blends"])
app.include_router(trans_sum_router,        prefix="/api",      tags=["trans_sum"])
app.include_router(vintrace_pull_router,    prefix="/api",      tags=["vintrace"])
app.include_router(trans_sum_sync_router,   prefix="/api",      tags=["trans_sum"])
app.include_router(meta_router,             prefix="/api/meta", tags=["meta"])
app.include_router(shipments_router,        prefix="/api",      tags=["shipments"]) # <--- NEW ROUTE
app.include_router(harvestload_agcode_router, prefix="/api", tags=["harvestload_agcode"])

# --- IMPROVED ERROR HANDLING VIA UTILS ---
app.exception_handler(StarletteHTTPException)(http_exception_handler)
app.exception_handler(RequestValidationError)(validation_exception_handler)
app.exception_handler(Exception)(generic_exception_handler)

# --- END FILE ---