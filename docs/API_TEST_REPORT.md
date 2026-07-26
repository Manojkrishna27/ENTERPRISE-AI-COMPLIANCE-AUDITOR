# REST API Audit & Test Coverage Report

**Project**: Enterprise AI Compliance & Contract Auditor  
**Framework**: FastAPI 0.110+  

---

## 🔌 API Endpoint Verification Matrix

| Router Path | Method | Purpose | Auth Required | Test Status |
|---|---|---|---|---|
| `/api/health` | GET | Liveness probe | Public | ✅ PASSED |
| `/api/ready` | GET | Infrastructure readiness probe | Public | ✅ PASSED |
| `/metrics` | GET | Prometheus metrics exporter | Public | ✅ PASSED |
| `/api/auth/departments` | GET | Public registration department list | Public | ✅ PASSED |
| `/api/auth/register` | POST | User registration | Public | ✅ PASSED |
| `/api/auth/login` | POST | User authentication & JWT issuance | Public | ✅ PASSED |
| `/api/auth/me` | GET | Current user profile | Bearer JWT | ✅ PASSED |
| `/api/auth/logout` | POST | Token revocation & Redis blocklist | Bearer JWT | ✅ PASSED |
| `/api/contracts/upload` | POST | Upload legal contract document | Bearer JWT | ✅ PASSED |
| `/api/contracts` | GET | List department contracts | Bearer JWT | ✅ PASSED |
| `/api/policies` | GET | List compliance policy standards | Bearer JWT | ✅ PASSED |
| `/api/admin/users` | GET | Admin user management | Admin Role | ✅ PASSED |
| `/api/admin/audit-logs` | GET | System security audit trail | Admin/Officer | ✅ PASSED |
| `/api/system/jobs/{id}` | GET | Async task status monitor | Bearer JWT | ✅ PASSED |
