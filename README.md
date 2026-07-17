# Enterprise AI Compliance & Contract Auditor

An advanced AI-powered SaaS platform designed to audit business contracts against global regulatory standards and internal compliance policies using **Retrieval-Augmented Generation (RAG)** and Large Language Models.

---

## 🌟 Key Features

- **Document Ingestion & Chunking**: Automatic high-fidelity parsing of contract and policy files (PDF/DOCX) into structured text sections with metadata (page numbers, paragraph indices).
- **RAG-Based AI Auditing**: Semantic search powered by **Qdrant Vector DB** and LLM clause analysis to locate non-compliant phrasing, missing standard contractual clauses (SCCs), and regulatory gaps.
- **Detailed Findings & Citation**: Exact context matches from contracts and policies with page number citations, risk levels (High, Medium, Low), explanation, business impact, and recommendations.
- **Executive PDF Report Generator**: On-the-fly, high-fidelity PDF report generation using **ReportLab**, featuring structured audit summaries and professional layouts.
- **Admin Workstation**: Complete administrative console to manage departments, users, policies, and view tenant-isolated audit logs.

---

## 🛠️ Tech Stack

- **Frontend**: React (SPA), Vite, Tailwind CSS (Vanilla CSS UI design), React Router.
- **Backend**: Flask (Python 3.11), SQLAlchemy ORM, Flask-JWT-Extended.
- **Vector DB**: Qdrant (Rust-based vector search).
- **Relational DB**: PostgreSQL (production) / SQLite (isolated testing).
- **Task Queue & Caching**: Redis.
- **Gateway & Load Balancer**: Nginx.

---

## 🚀 Getting Started

The platform is fully containerized and ready for one-command startup.

### Prerequisites

Ensure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 1. Configure Secrets

Create a `.env` file in the root directory (based on `.env.example`):

```bash
cp .env.example .env
```

Ensure you configure the `OPENAI_API_KEY` (or the system will automatically fall back to mock completions and local embeddings for isolated offline testing).

### 2. Start the Application

Run the following command to build and launch all services:

```bash
docker compose up --build
```

### 3. Database Auto-Seeding

On startup, the backend automatically runs database initialization and seeding. This creates the PostgreSQL tables and populates default departments and user roles.

---

## 🔐 Credentials & Roles

Once the containers are healthy, open your browser and navigate to:
👉 **`http://localhost`**

Log in using one of the following seeded corporate accounts:

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@company.com` | `admin123` | Full access, user/department administration. |
| **Compliance Officer** | `officer@company.com` | `officer123` | Policy management and global contract review. |
| **Legal Reviewer** | `legal@company.com` | `legal123` | Specific contract clause analysis and approvals. |
| **Auditor** | `auditor@company.com` | `auditor123` | Audit trail extraction and executive reporting. |
| **Viewer** | `viewer@company.com` | `viewer123` | Read-only access to contracts and findings. |

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy Database Schemas
│   │   ├── routers/      # API endpoints (auth, contracts, analysis, reports)
│   │   ├── services/     # OpenAI, Qdrant, S3/Local Storage, and Document Parser
│   │   └── utils/        # Token management, encryption, and helpers
│   ├── seed.py           # DB Seeding Script
│   └── wsgi.py           # Application Gateway Entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/   # Shared Layout components
│   │   ├── pages/        # Workstation views (Dashboard, Contracts, Search, Reports)
│   │   └── App.jsx       # React Router and application layout
│   └── vite.config.js    # Dev-server proxy config
├── nginx/
│   ├── nginx.conf        # Proxy router for Nginx
│   └── Dockerfile
└── docker-compose.yml    # Main container orchestrator configuration
```
