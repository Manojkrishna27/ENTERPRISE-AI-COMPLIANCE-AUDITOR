# Production Deployment Checklist

Use this step-by-step checklist to deploy the **Enterprise AI Compliance & Contract Auditor** to staging or production environments.

---

## 📋 Pre-Deployment Configuration

- [ ] Clone repository:
  ```bash
  git clone https://github.com/Manojkrishna27/ENTERPRISE-AI-COMPLIANCE-AUDITOR.git
  cd ENTERPRISE-AI-COMPLIANCE-AUDITOR
  ```
- [ ] Configure environment variables:
  ```bash
  cp .env.example .env
  ```
- [ ] Generate secure secrets in `.env`:
  - `SECRET_KEY`
  - `JWT_SECRET_KEY`
  - `OPENAI_API_KEY` or `GEMINI_API_KEY`
  - `EMAIL_VERIFICATION_ENABLED=false` (or `true` if SMTP configured)

---

## 🚀 Container Deployment

- [ ] Build and start the full production stack:
  ```bash
  docker compose -f docker-compose.prod.yml up -d --build
  ```

---

## ✅ Post-Deployment Verification

- [ ] Check container statuses:
  ```bash
  docker compose -f docker-compose.prod.yml ps
  ```

- [ ] Test application liveness probe:
  ```bash
  curl http://localhost/api/health
  ```

- [ ] Test deep infrastructure readiness probe:
  ```bash
  curl http://localhost/api/ready
  ```

- [ ] Inspect Prometheus metrics:
  ```bash
  curl http://localhost/metrics
  ```

- [ ] Access Frontend UI at `http://localhost`.
