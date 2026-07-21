from flask import Blueprint, jsonify, current_app
from app.database import db
from app.services.redis_service import redis_service
from app.services.qdrant_service import qdrant_service
from app.ai_config import ai_config
import time
import datetime

system_bp = Blueprint('system', __name__)

START_TIME = time.time()

@system_bp.route('/health', methods=['GET'])
def health_check():
    """
    Lightweight health check
    ---
    tags:
      - System
    responses:
      200:
        description: System is healthy
    """
    uptime = time.time() - START_TIME
    return jsonify({
        "status": "healthy",
        "backend": "healthy",
        "version": "1.0.0",
        "uptime": str(datetime.timedelta(seconds=int(uptime)))
    }), 200

@system_bp.route('/ready', methods=['GET'])
def ready_check():
    """
    Deep readiness validation
    ---
    tags:
      - System
    responses:
      200:
        description: All systems operational
      503:
        description: One or more systems are unavailable
    """
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
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        health_status["database"] = "unhealthy"
        is_ready = False
        
    # 2. Check Redis
    try:
        if not redis_service.redis_client.ping():
            raise Exception()
    except Exception:
        health_status["redis"] = "unhealthy"
        is_ready = False
        
    # 3. Check Qdrant
    try:
        if qdrant_service.client is None:
            health_status["qdrant"] = "fallback_memory"
            # We don't fail readiness for memory fallback if allowed, 
            # but in production we want to ensure Qdrant is connected.
            if current_app.config.get('FLASK_ENV') == 'production':
                health_status["qdrant"] = "unhealthy"
                is_ready = False
        else:
            qdrant_service.client.get_collections()
    except Exception:
        health_status["qdrant"] = "unhealthy"
        is_ready = False
        
    # 4. Check AI Provider (Ensure API Key exists and config resolved)
    if not ai_config.api_key:
        health_status["llm"] = "unhealthy"
        is_ready = False
        
    if not is_ready:
        health_status["status"] = "unhealthy"
        return jsonify(health_status), 503
        
    return jsonify(health_status), 200
