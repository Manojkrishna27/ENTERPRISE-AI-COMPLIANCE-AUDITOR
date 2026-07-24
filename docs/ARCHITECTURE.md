# Architecture & System Design

## System Architecture

The Enterprise AI Compliance & Contract Auditor platform uses a microservices architecture to achieve high availability, security, and performance.

```text
                                  +-------------------+
                                  |    Client Browser |
                                  +---------+---------+
                                            | (HTTPS / REST)
                                            v
                                  +-------------------+
                                  |   Nginx Proxy     |
                                  +---------+---------+
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
               +-------------------+                 +-------------------+
               |  React Frontend   |                 |   Flask Backend   |
               |  (Port 3000)      |                 |   (Port 5001)     |
               +-------------------+                 +---------+---------+
                                                               |
               +-------------------+-------------------+-------+-------+
               |                   |                   |               |
               v                   v                   v               v
     +-------------------+ +---------------+ +-------------------+ +--------------+
     | PostgreSQL 15     | | Redis Cache   | | Qdrant Vector DB  | | Gemini/OpenAI|
     | (Relational Data) | | (JWT / Rate)  | | (Embeddings 768)  | | LLM APIs   |
     +-------------------+ +---------------+ +-------------------+ +--------------+
```

---

## Key Components

### 1. Frontend Tier
- **Framework**: React 18 powered by Vite.
- **Styling**: Tailwind CSS for responsive visual layouts.
- **State & Data**: React Router DOM & Axios API clients.

### 2. Backend API Tier
- **Framework**: Python 3.11 with Flask, served via `gunicorn` in production.
- **Security**: JWT authentication with Redis-backed token revocation/blocklisting.
- **Rate Limiting**: `Flask-Limiter` enforced on authentication and inference routes.

### 3. Data Tier
- **PostgreSQL**: Stores relational user metadata, contract metadata, and audit logs.
- **Qdrant**: High-performance vector database with Matryoshka 768-dim vector indexes.
- **Redis**: In-memory caching, session management, rate-limiting counters, and token blocklists.

---

## Diagrams

- System Architecture Diagram: [`docs/diagrams/system-architecture.puml`](./diagrams/system-architecture.puml)
- Deployment Architecture: [`docs/diagrams/deployment-architecture.puml`](./diagrams/deployment-architecture.puml)
- Database ERD: [`docs/diagrams/database-erd.puml`](./diagrams/database-erd.puml)
- Authentication Flow: [`docs/diagrams/authentication-flow.puml`](./diagrams/authentication-flow.puml)
