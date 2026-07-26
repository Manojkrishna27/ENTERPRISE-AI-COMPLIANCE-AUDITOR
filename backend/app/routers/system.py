import time
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.services.redis_service import redis_service
from app.services.qdrant_service import qdrant_service
from app.ai_config import ai_config

router = APIRouter(prefix="/api", tags=["System"])

START_TIME = time.time()

@router.get("/health", summary="Lightweight health check", description="Return simple 200 OK status for load balancers")
def health_check():
    uptime = time.time() - START_TIME
    return {
        "status": "healthy",
        "backend": "healthy",
        "version": "1.0.0",
        "uptime": str(datetime.timedelta(seconds=int(uptime)))
    }

@router.get("/ready", summary="Deep readiness validation", description="Validate operational readiness of Postgres, Redis, Qdrant, and LLM services")
def ready_check(db: Session = Depends(get_db)):
    uptime = time.time() - START_TIME
    health_status = {
        "status": "healthy",
        "backend": "healthy",
        "database": "healthy",
        "redis": "healthy",
        "qdrant": "healthy",
        "llm": "healthy",
        "version": "1.0.0",
        "uptime": str(datetime.timedelta(seconds=int(uptime)))
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
        if not redis_service.redis_client or not redis_service.redis_client.ping():
            raise Exception("Redis ping failed")
    except Exception:
        health_status["redis"] = "unhealthy"
        is_ready = False
        
    # 3. Check Qdrant
    try:
        if qdrant_service.client is None:
            health_status["qdrant"] = "fallback_memory"
        else:
            qdrant_service.client.get_collections()
    except Exception:
        health_status["qdrant"] = "unhealthy"
        is_ready = False
        
    # 4. Check AI Provider Key
    if not ai_config.api_key:
        health_status["llm"] = "unhealthy"
        is_ready = False
        
    if not is_ready:
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)
        
    return health_status
