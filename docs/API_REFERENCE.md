# API Reference
## Overview
The Enterprise AI Compliance Auditor uses a RESTful API powered by Flask. All requests must be authenticated using JWTs except for login/register and health endpoints. 

## Swagger Documentation
Interactive Swagger UI is available natively. Run the application and navigate to:
**URL:** `http://localhost:5000/apidocs`

## Standard Error Format
All exceptions and API errors return a standard JSON shape.
```json
{
    "status": "error",
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Unexpected server error.",
    "request_id": "89052b04-f064-4e2f-b472-...",
    "timestamp": "2026-07-21T18:00:00.000Z"
}
```

## Endpoints Summary

### Authentication (`/api/auth`)
- `POST /register`: Registers a new user. Rate limit: 5/min
- `POST /login`: Generates JWT access tokens. Rate limit: 5/min
- `POST /logout`: Blocklists the active JWT. Rate limit: 10/min

### Contracts (`/api/contracts`)
- `GET /`: Lists all uploaded contracts with RBAC filtering. Rate limit: 60/min
- `POST /`: Uploads, parses, chunks, embeds, and indexes a PDF/DOCX. Rate limit: 10/min

### System (`/api`)
- `GET /health`: Shallow liveness probe. Rate limit: Unlimited
- `GET /ready`: Deep readiness probe checking DB, Redis, Qdrant, and LLM APIs.

*For complete schema parameters and responses, refer to the Swagger UI (`/apidocs`).*
