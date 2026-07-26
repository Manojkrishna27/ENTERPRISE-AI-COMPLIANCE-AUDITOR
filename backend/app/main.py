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
from app.core.database import Base, engine, SessionLocal, db
from app.models.user import User, Department
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

def init_db_and_seed():
    print("\n--------------------------------------------------")
    print(f"[STARTUP] Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"[STARTUP] Mode: {'Docker Container' if settings.is_docker else 'Local Environment'}")
    print(f"[STARTUP] Email Verification: {'ENABLED' if settings.EMAIL_VERIFICATION_ENABLED else 'DISABLED (Auto-Verify)'}")
    
    # 1. Database Table Initialization
    try:
        Base.metadata.create_all(bind=engine)
        print("[STARTUP] ✅ Database connected & tables initialized")
    except Exception as e:
        print(f"[STARTUP] ❌ Database initialization failed: {e}")

    # 2. Idempotent Seeding (Departments & Admin)
    db_sess = SessionLocal()
    try:
        # Seed Departments if empty
        dept_count = db_sess.query(Department).count()
        if dept_count == 0:
            default_depts = [
                Department(name="Legal", description="Legal compliance & contract management"),
                Department(name="Compliance", description="Corporate policy & regulatory compliance"),
                Department(name="Procurement", description="Vendor & supplier agreements"),
                Department(name="Engineering", description="Software & technology operations"),
                Department(name="HR", description="Human resources & employment policies"),
                Department(name="Executive", description="Executive leadership & governance")
            ]
            db_sess.add_all(default_depts)
            db_sess.commit()
            print("[STARTUP] ✅ Departments seeded (Legal, Compliance, Procurement, Engineering, HR, Executive)")
        else:
            print(f"[STARTUP] ℹ️ Departments already initialized ({dept_count} departments found)")

        # Seed System Admin if no Admin exists
        admin_user = db_sess.query(User).filter(User.role == 'Admin').first()
        if not admin_user:
            admin_dept = db_sess.query(Department).filter(Department.name == 'Legal').first()
            admin = User(
                email=settings.DEFAULT_ADMIN_EMAIL,
                full_name="System Administrator",
                role="Admin",
                department_id=admin_dept.id if admin_dept else None,
                is_active=True,
                is_verified=True
            )
            admin.set_password(settings.DEFAULT_ADMIN_PASSWORD)
            db_sess.add(admin)
            db_sess.commit()
            print(f"[STARTUP] ✅ Default System Admin created: {settings.DEFAULT_ADMIN_EMAIL}")
        else:
            print(f"[STARTUP] ℹ️ System Admin status: Admin active ({admin_user.email})")
    except Exception as e:
        db_sess.rollback()
        print(f"[STARTUP] ⚠️ Seeding warning: {e}")
    finally:
        db_sess.close()

    # 3. Infrastructure Diagnostics
    try:
        from app.services.qdrant_service import qdrant_service
        if qdrant_service.is_connected():
            print(f"[STARTUP] ✅ Qdrant connected at {qdrant_service.host}:{qdrant_service.port}")
        else:
            print("[STARTUP] ℹ️ Qdrant using in-memory vector DB fallback")
    except Exception as e:
        print(f"[STARTUP] ⚠️ Qdrant status: {e}")

    try:
        from app.services.redis_service import redis_service
        if redis_service.is_connected():
            print("[STARTUP] ✅ Redis connected (JWT blocklisting active)")
        else:
            print("[STARTUP] ℹ️ Redis running in fallback mode")
    except Exception as e:
        print(f"[STARTUP] ℹ️ Redis status: {e}")

    try:
        from app.services.providers.factory import get_llm_provider
        provider = get_llm_provider()
        print(f"[STARTUP] ✅ AI Provider initialized: {provider.__class__.__name__}")
    except Exception as e:
        print(f"[STARTUP] ⚠️ AI Provider warning: {e}")

    print("--------------------------------------------------\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.USE_LOCAL_STORAGE:
        os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
    init_db_and_seed()
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

from fastapi import Response
from app.core.metrics import record_http_request, generate_prometheus_metrics

# Request ID, Security Headers & Metrics Middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    
    # Record Prometheus metrics
    record_http_request(request.url.path, response.status_code, process_time)
    return response

@app.get("/metrics", summary="Prometheus metrics exporter", description="Export system runtime and performance metrics in Prometheus text format")
def get_metrics():
    metrics_data = generate_prometheus_metrics()
    return Response(content=metrics_data, media_type="text/plain")

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
