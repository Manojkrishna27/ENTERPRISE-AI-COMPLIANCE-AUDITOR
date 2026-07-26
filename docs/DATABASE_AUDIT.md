# Database Architecture & Query Audit Report

**Project**: Enterprise AI Compliance & Contract Auditor  
**Engine**: PostgreSQL 15 / SQLite 3  
**ORM**: SQLAlchemy 2.0  
**Migrations**: Alembic 1.13+  

---

## 📐 Schema Integrity & Indexes

### Tables Overview:
1. `users` — Primary key UUID, unique index on `email`, foreign key `department_id`.
2. `departments` — Primary key UUID, unique index on `name`.
3. `contracts` — Foreign keys `department_id`, `owner_id`; indexed on foreign keys for high-speed queries.
4. `policies` — Foreign key `department_id`; indexed for rapid policy retrieval.
5. `audit_logs` — Foreign key `user_id`; indexed on `created_at DESC` for fast admin log rendering.
6. `reports` — Foreign key `contract_id`, `created_by`.
7. `notifications` — Foreign key `user_id`.

---

## ⚡ Performance & Connection Pooling

- **Connection Pool**:
  - `pool_size = 10`
  - `max_overflow = 20`
  - `pool_recycle = 3600`
  - `pool_pre_ping = True`
- **N+1 Query Prevention**: Eager loading (`joinedload`) applied across router methods.
