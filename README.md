<div align="center">
  <img src="./screenshots/Logo.png" alt="Enterprise AI Compliance Auditor Logo" width="550">

  <h1>Enterprise AI Compliance & Contract Auditor</h1>
  <p><i>A production-grade, multi-tenant AI system for automated legal contract ingestion, policy comparison, and risk analysis using advanced RAG.</i></p>

  <!-- Badges -->
  <a href="https://github.com/Manojkrishna27/ENTERPRISE-AI-COMPLIANCE-AUDITOR/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python Version"></a>
  <a href="https://react.dev"><img src="https://img.shields.io/badge/React-18.2-blue?style=flat-square&logo=react" alt="React"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square&logo=flask" alt="Flask"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Enabled-blue?style=flat-square&logo=docker" alt="Docker"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT"></a>

  <br /><br />

  <a href="#-key-features">Features</a> •
  <a href="#-architecture--tech-stack">Architecture</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-testing--quality-assurance">Testing</a> •
  <a href="#-security--compliance">Security</a> •
  <a href="#-detailed-documentation">Docs</a>
</div>

<br />

## 📖 Overview

**Enterprise AI Compliance & Contract Auditor** is a full-stack, enterprise-ready SaaS platform that automates one of the most time-consuming parts of legal operations: contract review.

It ingests legal contracts (PDF, DOCX), semantically parses them, and uses **Retrieval-Augmented Generation (RAG)** to compare them against internal corporate policy. The system flags high-risk liabilities, missing mandatory clauses, and compliance gaps — cutting manual review time from hours to minutes while removing human error from the process.

Built with **security**, **multi-tenancy**, and **scalability** as first-class concerns, the platform is designed to hold up in Fortune 500 production environments, not just demos.

---

## 🔄 End-to-End RAG Workflow

From document upload to AI-powered compliance insight — the full pipeline, in one diagram:

<div align="center">
  <img src="./screenshots/rag-workflow.png" alt="End-to-End RAG Workflow" width="100%">
</div>

<p align="center"><i>8-stage pipeline: Document Ingestion → Text Chunking → Embedding Generation → Vector Storage → User Query → Retrieval → AI Generation → Response & Citations — backed by dedicated Auth, Database, Cache, Storage, Observability, and Security layers.</i></p>

---

## 📸 Screenshots

| Dashboard & Overview | Contract Upload & Viewer |
| :---: | :---: |
| <img src="./screenshots/Dashboard.png" alt="Dashboard" width="400"> | <img src="./screenshots/viewer.png" alt="Contract Viewer" width="400"> |
| **RAG Copilot & Audit** | **Generated Reports** |
| <img src="./screenshots/AI%20compliace%20audit.png" alt="AI Compliance Audit" width="400"> | <img src="./screenshots/report.png" alt="Reports" width="400"> |
| **Policy Standards** | **Secure Login** |
| <img src="./screenshots/Policy%20standard.png" alt="Policies" width="400"> | <img src="./screenshots/Login.png" alt="Login" width="400"> |

---

## ✨ Key Features

| | |
|---|---|
| 🧠 **Enterprise RAG Pipeline** | High-fidelity semantic chunking using PyMuPDF and LlamaIndex. |
| ⚡ **Dynamic AI Adapters** | Provider-agnostic architecture that dynamically supports Google Gemini (`gemini-1.5-flash`, `gemini-embedding-2`) and OpenAI. |
| 🎯 **Matryoshka Representation Vectors** | 768-dimensional Qdrant embeddings tuned for precise semantic spatial relations during retrieval. |
| 🔐 **Multi-Tenant Security** | Strict Role-Based Access Control (RBAC), `department_id`-level Qdrant isolation, and Redis-backed JWT blocklisting. |
| 🛡️ **Production Hardened** | Built-in request tracing (`X-Request-ID`), standardized global error responses, `Flask-Limiter` rate limiting, and deep Kubernetes-style `/ready` probes. |
| 📊 **Real-Time Interactive Dashboard** | Built with React, Recharts, and Tailwind CSS for seamless data visualization and Copilot interaction. |

---

## 🏗 Architecture & Tech Stack

The platform uses a containerized microservices architecture for isolated scaling, security, and maintainability.

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS & Headless UI
- **Routing & State**: React Router DOM, Axios
- **Data Visualization**: Recharts

### Backend
- **Core API**: Python 3.11, Flask, Gunicorn
- **AI Core**: LlamaIndex, Google Gemini API / OpenAI
- **Document Processing**: PyMuPDF, python-docx

### Infrastructure & Data Tier
- **Relational DB**: PostgreSQL 15 (ACID compliant)
- **Vector DB**: Qdrant (high-performance semantic search)
- **Cache & Rate Limiting**: Redis (JWT blocklisting, `Flask-Limiter`)
- **Deployment**: Docker Compose, Nginx reverse proxy (load balancing)

*(See [`docs/diagrams/system-architecture.puml`](./docs/diagrams/system-architecture.puml) for the full architectural diagram.)*

---

## 📂 Repository Structure

```text
.
├── backend/                  # Flask REST API, Services, and AI Providers
│   ├── app/                  # Application code (Routers, Models, Services)
│   ├── tests/                # Pytest Suite
│   ├── Dockerfile            # Backend container definition (non-root)
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React Vite SPA
│   ├── src/                  # React components, pages, and context
│   ├── Dockerfile            # Frontend container definition
│   └── package.json          # Node dependencies
├── docs/                     # Comprehensive Markdown and PlantUML documentation
│   └── diagrams/             # Architecture & workflow diagrams (rag-workflow.png, etc.)
├── nginx/                    # Nginx reverse proxy configuration
├── docker-compose.yml        # Orchestration for the entire stack
└── .env.example              # Environment variables template
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose installed
- An API key from Google Gemini or OpenAI

### 1. Configuration

Clone the repository and set up your environment variables:

```bash
git clone https://github.com/Manojkrishna27/ENTERPRISE-AI-COMPLIANCE-AUDITOR.git
cd ENTERPRISE-AI-COMPLIANCE-AUDITOR

# Create the environment file
cp .env.example .env
```

Edit `.env` to add your `OPENAI_API_KEY` (also used for Gemini access depending on configuration), and generate secure values for `SECRET_KEY` and `JWT_SECRET_KEY`.

### 2. Deployment

The system is fully containerized. Spin up the entire stack with Docker Compose:

```bash
docker compose up -d --build
```

### 3. Verify Health

Confirm all subsystems (PostgreSQL, Redis, Qdrant, AI API) are operational via the deep readiness probe:

```bash
curl http://localhost:5001/api/ready
```

### 4. Access the Application

| Service | URL |
|---|---|
| Frontend Dashboard | `http://localhost:3000` |
| Swagger API Docs | `http://localhost:5001/apidocs` |

---

## 🧪 Testing & Quality Assurance

The backend ships with a comprehensive Pytest suite that mocks external dependencies to validate the RAG pipeline, chunking logic, and auth mechanisms.

Run the automated tests with:

```bash
docker compose exec backend pytest
```

---

## 🔐 Security & Compliance

This project follows strictly enforced OWASP standards:

- **Authentication** — JWT with Redis-backed blocklisting for secure, immediate logout.
- **Rate Limiting** — Granular protection on authentication, upload, and AI-inference endpoints to prevent abuse and quota exhaustion.
- **Payload Validation** — `MAX_CONTENT_LENGTH` restrictions and secure filename validation to prevent path traversal attacks.
- **Execution Isolation** — Docker containers run as non-root `appuser` to prevent privilege escalation.

---

## 📚 Detailed Documentation

Dive deeper into the system's architecture and capabilities in the `docs/` directory:

- 📖 [Architecture & System Design](./docs/ARCHITECTURE.md)
- 🔌 [API Reference](./docs/API_REFERENCE.md)
- 🧠 [RAG Workflow](./docs/RAG_WORKFLOW.md)
- 🛡️ [Security Threat Model](./docs/SECURITY.md)
- 🏆 [Final Production Report](./docs/FINAL_PRODUCTION_REPORT.md)

---

## 🤝 Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

<div align="center">
  <b>Built for the Modern Enterprise by Forward Deployed Engineering</b>
</div>
