import os
import uuid
import time
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import db
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from app.routers import (
    auth,
    contracts,
    policies,
    analysis,
    reports,
    search,
    system,
    admin,
    dashboard
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.USE_LOCAL_STORAGE:
        os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
    try:
        db.create_all()
    except Exception as e:
        print(f"Database table initialization warning: {e}")
    yield

app = FastAPI(
    title="Enterprise AI Compliance & Contract Auditor API",
    description="Production-grade Enterprise AI Compliance & Contract Auditor REST API powered by FastAPI, LlamaIndex, Qdrant, and Gemini/OpenAI.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID & Timing Middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Global Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include Routers
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(policies.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(system.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
