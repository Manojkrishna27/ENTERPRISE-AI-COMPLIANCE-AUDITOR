from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
import datetime

rag_logger = logging.getLogger("rag_auditor")

async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "msg": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "status": "error",
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "request_id": request_id,
            "timestamp": datetime.datetime.utcnow().isoformat()
        },
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "")
    errors = exc.errors()
    msg = errors[0].get("msg") if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "msg": msg,
            "status": "error",
            "message": "Invalid request payload",
            "details": errors,
            "request_id": request_id,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "")
    rag_logger.error(f"[{request_id}] Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "msg": "Internal server error",
            "status": "error",
            "message": "Unexpected server error.",
            "error": str(exc),
            "request_id": request_id,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    )
