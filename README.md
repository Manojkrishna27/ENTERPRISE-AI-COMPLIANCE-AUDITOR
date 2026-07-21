# Enterprise AI Compliance & Contract Auditor

A production-grade, multi-tenant AI system designed to automatically ingest legal contracts, compare them against corporate policies using advanced Retrieval-Augmented Generation (RAG), and identify high-risk liabilities, missing clauses, and compliance violations.

## 🚀 Key Features
* **Enterprise RAG Pipeline**: High-fidelity chunking using PyMuPDF and LlamaIndex.
* **Dynamic AI Adapters**: Provider-agnostic architecture dynamically supporting Google Gemini (`gemini-1.5-flash`, `gemini-embedding-2`) and OpenAI.
* **Matryoshka Representation Vectors**: Precision 768-dimensional Qdrant embeddings ensuring perfect semantic spatial relations.
* **Multi-Tenant Security**: Strict Role-Based Access Control (RBAC), `department_id` Qdrant isolation, and Redis-backed JWT blocklisting.
* **Production Hardened**: Built-in Request Tracing (`X-Request-ID`), standardized Error APIs, `Flask-Limiter` rate limiting, and deep Kubernetes-style `/ready` probes.

## 🏗 Architecture
This platform utilizes a containerized microservices architecture with a React 19 Frontend and Flask Gunicorn Backend.

*(See `docs/diagrams/system-architecture.puml` for the full visual diagram)*

### Core Technologies
- **Backend API:** Python 3.11, Flask, Gunicorn
- **Database:** PostgreSQL (Relational), Qdrant (Vectors), Redis (Rate Limiting & Cache)
- **AI Core:** LlamaIndex, Google Gemini API
- **Deployment:** Docker Compose, Nginx Reverse Proxy

## 📚 Documentation
Comprehensive documentation can be found in the `docs/` directory:
- `ARCHITECTURE.md` - System layout and data flow
- `API_REFERENCE.md` - Complete API guidelines
- `RAG_WORKFLOW.md` - Deep dive into embedding generation
- `SECURITY.md` - Threat modeling and RBAC definitions
- `FINAL_PRODUCTION_REPORT.md` - End-to-end quality audit

**Swagger UI:** Available at `http://localhost:5000/apidocs` when the system is running.

## ⚙️ Quick Start

### 1. Configuration
Create a `.env` file based on the provided template:
```env
OPENAI_API_KEY=your_gemini_or_openai_key
DATABASE_URL=postgresql://postgres:postgres@db:5432/contract_compliance
QDRANT_HOST=qdrant
REDIS_URL=redis://redis:6379/0
```

### 2. Docker Deployment
The system is fully containerized with healthchecks and non-root users:
```bash
docker compose up -d --build
```

### 3. Verify Health
Ensure all subsystems (DB, Redis, Qdrant, AI) are operational:
```bash
curl http://localhost:5000/api/ready
```

## 🧪 Testing
The backend features a comprehensive Pytest suite mocking dependencies to validate the RAG pipeline and Auth mechanisms.
```bash
docker compose exec backend pytest
```

## 🔐 License & Security
This project follows strictly enforced OWASP standards, preventing path traversals, enforcing CORS, and validating maximum content payload sizes.

---
**Maintained by:** Enterprise Forward Deployed Engineering Team
