# Security Threat Model & Safeguards

## Overview

The Enterprise AI Compliance Auditor is built with strict multi-tenant isolation, defense-in-depth API protection, and OWASP security standards.

---

## Core Security Controls

### 1. Authentication & Session Security
- **JWT Authentication**: Stateless bearer tokens signed with secret keys (`HS256`).
- **Token Blocklisting**: Active logouts instantly invalidate tokens by indexing JTI tokens in Redis with exact TTL expirations.

### 2. Multi-Tenant Isolation
- **Role-Based Access Control (RBAC)**: Enforced via decorating endpoints (`@login_required`, `@admin_required`).
- **Payload Filter Isolation**: Vector database queries force `department_id` filters on Qdrant collections to prevent cross-tenant vector data leakage.

### 3. Rate Limiting & Denial of Service (DoS) Protection
- **Flask-Limiter Integration**: Dedicated rate limits on authentication endpoints (5 req/min), document upload (10 req/min), and LLM copilot queries.
- **Payload Size Limits**: Strict `MAX_CONTENT_LENGTH` enforcement (16MB max upload size).

### 4. Container & Infrastructure Hardening
- **Non-Root User Execution**: Backend container runs under dedicated `appuser` (UID 10001).
- **Network Isolation**: Docker Compose internal bridge networks restrict external port exposure to Nginx proxy.
