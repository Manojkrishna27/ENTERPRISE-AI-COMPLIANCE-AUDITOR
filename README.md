# 🛡️ Enterprise AI Compliance & Contract Auditor

> AI-powered Enterprise Compliance Platform for automated contract review using **Retrieval-Augmented Generation (RAG)**, semantic search, and Large Language Models.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![React](https://img.shields.io/badge/React-18-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![AWS](https://img.shields.io/badge/AWS-Cloud-orange)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 📖 Overview

Enterprise organizations process thousands of contracts every year.

Legal and compliance teams spend significant time reviewing every document against:

- Internal company policies
- GDPR
- ISO 27001
- SOC 2
- Vendor security standards
- Procurement rules
- Privacy regulations

Manual review is expensive, slow, and prone to human error.

**Enterprise AI Compliance & Contract Auditor** automates this workflow using AI.

The system compares uploaded contracts against enterprise policies using **Retrieval-Augmented Generation (RAG)**, identifies compliance violations, explains the findings, highlights supporting evidence, and generates executive-ready reports.

---

# 🎯 Problem Statement

Traditional contract reviews require hours of manual work.

Example:

Company Policy

> Vendors must report security incidents within **24 hours**.

Vendor Contract

> Vendor may notify the company within **7 days**.

The platform automatically detects this conflict, explains why it is non-compliant, highlights the relevant clauses, and recommends compliant wording.

---

# ✨ Core Features

## 📄 Smart Document Processing

- Upload PDF and DOCX contracts
- Upload internal compliance policies
- Automatic text extraction using PyMuPDF
- Semantic chunking
- Metadata preservation
- Page number tracking
- Paragraph indexing

---

## 🤖 AI Compliance Analysis

Automatically detects

- Missing clauses
- Security policy violations
- GDPR issues
- Privacy risks
- Weak contractual language
- Vendor compliance risks
- Payment risks
- Confidentiality issues
- Regulatory gaps

Every finding includes

- Risk Level
- Explanation
- Business Impact
- Recommendation
- Confidence Score

---

## 🔍 Retrieval-Augmented Generation (RAG)

The platform

- Parses documents
- Creates embeddings
- Stores vectors inside Qdrant
- Retrieves only relevant policy sections
- Sends retrieved context to the LLM
- Produces explainable compliance analysis

---

## 📌 Citation Highlighting

Every AI finding links directly to

- Contract Page
- Paragraph
- Policy Page
- Policy Paragraph

Clicking **Show Evidence**

✔ Opens the PDF

✔ Scrolls automatically

✔ Highlights the exact clause

✔ Displays the matching policy side-by-side

---

## 📊 Executive Dashboard

Monitor

- Compliance Score
- High-Risk Contracts
- AI Findings
- Uploaded Policies
- Recent Analyses
- Department Statistics
- Risk Distribution

---

## 📑 Executive PDF Reports

Generate professional reports containing

- Executive Summary
- Compliance Score
- Risk Analysis
- Clause-by-Clause Review
- AI Recommendations
- Audit Trail

---

## 🔐 Enterprise Authentication

- JWT Authentication
- Password Hashing
- Role-Based Access Control

Supported Roles

- System Admin
- Compliance Officer
- Legal Reviewer
- Auditor
- Viewer

---

## 🏢 Administration

Manage

- Users
- Departments
- Contracts
- Policies
- Reports
- Audit Logs
- AI Usage

---

# 🏗 System Architecture

```
                  React Frontend
                         │
                         ▼
                 Flask REST API
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 PostgreSQL          Redis Cache      Qdrant
        │                                 │
        └──────────────┬──────────────────┘
                       ▼
               OpenAI + LlamaIndex
                       │
                       ▼
             AI Compliance Analysis
                       │
                       ▼
          Executive Reports & Dashboard
```

---

# ⚙️ Technology Stack

## Frontend

- React (JSX)
- Vite
- Tailwind CSS
- React Router
- Axios

## Backend

- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate

## AI

- OpenAI API
- LlamaIndex
- Qdrant

## Database

- PostgreSQL

## Cache

- Redis

## Document Processing

- PyMuPDF
- python-docx

## Infrastructure

- Docker
- Docker Compose
- Nginx
- AWS EC2
- AWS S3
- Linux

---

# 📂 Project Structure

```
backend/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── rag/
│   ├── auth/
│   ├── utils/
│   └── config/
│
├── migrations/
├── seed.py
└── run.py

frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── context/
│   ├── services/
│   └── App.jsx

nginx/
docker-compose.yml
README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/yourusername/enterprise-ai-compliance-auditor.git

cd enterprise-ai-compliance-auditor
```

---

## Configure Environment

```bash
cp .env.example .env
```

Configure

```
OPENAI_API_KEY=

POSTGRES_DB=

POSTGRES_USER=

POSTGRES_PASSWORD=

JWT_SECRET_KEY=
```

---

## Start Application

```bash
docker compose up --build
```

---

Application URLs

Frontend

```
http://localhost
```

Backend

```
http://localhost:5000
```

Swagger

```
http://localhost:5000/swagger
```

---

# 🔑 Demo Credentials

| Role | Email | Password |
|-------|-------|----------|
| Admin | admin@company.com | admin123 |
| Compliance Officer | officer@company.com | officer123 |
| Legal Reviewer | legal@company.com | legal123 |
| Auditor | auditor@company.com | auditor123 |
| Viewer | viewer@company.com | viewer123 |

---

# 🔄 AI Workflow

```
Upload Contract
        │
        ▼
Extract Text
        │
        ▼
Chunk Document
        │
        ▼
Generate Embeddings
        │
        ▼
Store in Qdrant
        │
        ▼
Retrieve Policies
        │
        ▼
LLM Analysis
        │
        ▼
Compliance Report
        │
        ▼
Citation Highlighting
```

---

# 📈 Future Enhancements

- Multi-Tenant SaaS Architecture
- SSO (Google, Microsoft Entra ID, Okta)
- AI Chat Copilot
- Version Comparison
- Policy Impact Analysis
- Background Job Processing
- Prometheus & Grafana Monitoring
- Kubernetes Deployment
- Multi-Model LLM Support

---

# 🧪 Testing

```bash
docker compose up

Upload Policy

Upload Contract

Run AI Analysis

View Findings

Generate Report
```

---

# 📸 Screenshots

> Add screenshots here

- Login
- Dashboard
- Contract Upload
- Policy Library
- AI Findings
- Citation Viewer
- Reports

---

# 📄 License

MIT License

---

# 👨‍💻 Author

**Manojkrishna M**

B.Tech Artificial Intelligence & Data Science

Enterprise AI • Cloud • Flask • React • AWS • Docker
