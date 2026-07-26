import datetime
import time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai_config import ai_config
from app.core.database import get_db
from app.services.background_tasks import task_manager
from app.services.qdrant_service import qdrant_service
from app.services.redis_service import redis_service
from app.services.s3_service import s3_service

router = APIRouter(prefix="/api", tags=["System"])

START_TIME = time.time()


@router.get(
    "/health",
    summary="Lightweight health check",
    description="Return simple 200 OK status for Kubernetes liveness probes",
)
def health_check():
    uptime = time.time() - START_TIME
    return {
        "status": "healthy",
        "backend": "healthy",
        "version": "1.0.0",
        "uptime": str(datetime.timedelta(seconds=int(uptime))),
    }


@router.get(
    "/ready",
    summary="Deep readiness validation",
    description="Validate operational readiness of Postgres, Redis, Qdrant, Storage, and LLM services",
)
def ready_check(db: Session = Depends(get_db)):
    uptime = time.time() - START_TIME
    health_status = {
        "status": "healthy",
        "backend": "healthy",
        "database": "healthy",
        "redis": "healthy",
        "qdrant": "healthy",
        "storage": "healthy",
        "llm": "healthy",
        "version": "1.0.0",
        "uptime": str(datetime.timedelta(seconds=int(uptime))),
    }

    is_ready = True

    # 1. Check Database
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        health_status["database"] = "unhealthy"
        is_ready = False

    # 2. Check Redis
    try:
        if not redis_service.is_connected():
            health_status["redis"] = "fallback_memory"
    except Exception:
        health_status["redis"] = "unhealthy"

    # 3. Check Qdrant
    try:
        if not qdrant_service.is_connected():
            health_status["qdrant"] = "fallback_memory"
    except Exception:
        health_status["qdrant"] = "unhealthy"

    # 4. Check Storage
    try:
        if not s3_service.is_connected():
            health_status["storage"] = "unhealthy"
    except Exception:
        health_status["storage"] = "unhealthy"

    # 5. Check AI Provider Key
    if not ai_config.api_key:
        health_status["llm"] = "unhealthy"
        is_ready = False

    if not is_ready:
        health_status["status"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status
        )

    return health_status


@router.get(
    "/system/jobs/{job_id}",
    summary="Get background job status",
    description="Fetch background job progress and status details",
)
def get_job_status(job_id: str):
    job = task_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.post(
    "/system/jobs/{job_id}/retry",
    summary="Retry failed background job",
    description="Re-queue a failed background job for execution",
)
def retry_job(job_id: str):
    success = task_manager.retry_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or retry unsupported",
        )
    return {"msg": "Job re-queued successfully", "job_id": job_id}
