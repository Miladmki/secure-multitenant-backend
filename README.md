# Secure Multi-Tenant Backend

A **production-grade backend architecture** built with FastAPI, focused on **security-first design**, **multi-tenant isolation**, and **explicit authorization boundaries**.

This project is intentionally developed as a **real-world reference backend**, emphasizing correctness, clarity, and long-term maintainability over shortcuts.

---

## 🚦 Project Status

**Phase 2 — Multi-Tenant Architecture & Authorization (In Progress)**

### Completed
- ✅ Multi-tenant schema  
- ✅ Tenant-aware user model  
- ✅ Role model + `user_roles` (many-to-many)  
- ✅ Tenant isolation groundwork  
- ✅ Architecture stabilization (layers, imports, dependencies)  
- ✅ Error handling strategy  
- ✅ Clean Alembic migrations (baseline schema)  

### In Progress
- ⏳ Permission enforcement layer  
- ⏳ Tenant-scoped queries everywhere  
- ⏳ Role-based access control in routers  
- ⏳ Admin-only endpoints  

---

## 🎯 Core Objectives

- **Secure Authentication**
  - Password hashing (Argon2)
  - JWT access tokens
  - Refresh token lifecycle

- **Multi-Tenant Architecture**
  - Strong tenant boundaries
  - No cross-tenant data leakage
  - Tenant-aware queries by design

- **Authorization & Access Control**
  - Role-based authorization model
  - Deny-by-default policy
  - Explicit permission checks

- **Architecture Discipline**
  - Clear layer boundaries
  - Dependency-driven security
  - No hidden coupling

- **Operational Stability**
  - Reproducible database state
  - Migration discipline
  - Testable from zero state

---

## 🧱 Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic (batch-mode, SQLite-safe)
- **Auth**: JWT (access + refresh tokens)
- **Security**: Argon2, OAuth2 password flow
- **Database**: SQLite (dev), PostgreSQL (planned)
- **Testing**: Pytest

### Architectural Capabilities
- Multi-tenant schema
- Role-based authorization
- Tenant-aware refresh tokens
- Custom error-handling strategy
- Clean migration discipline

---

## 🗂 Project Structure

```
app/
├── api/
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       └── admin.py
│
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── deps.py
│   └── errors.py   # planned
│
├── models/
│   ├── user.py
│   ├── tenant.py
│   ├── role.py
│   ├── user_role.py
│   └── refresh_token.py
│
├── schemas/
│   └── user.py
│
├── main.py
│
docs/
├── error-handling.md
├── tenant-isolation.md
└── architecture.md  # planned
```

---

## 🔐 Authentication & Authorization Design

### Authentication
- OAuth2 password flow
- JWT access tokens
- Refresh tokens with rotation support

### Tenant-Aware Authentication
- Each user belongs to **exactly one tenant**
- Access tokens are implicitly tied to the user's tenant
- Refresh tokens are scoped per user & tenant
- Tenant isolation enforced in the dependency layer

### Authorization
- Role-based access control
- Many-to-many relationship between users and roles
- `require_role(...)` dependency for enforcement
- Deny-by-default: no role = no access

---

## 🧬 Database & Migrations

Alembic is **mandatory**.

### Migration Rules
- Batch-mode migrations (SQLite-safe)
- Full schema rebuild tested from zero
- No manual database edits
- All schema changes go through migrations
- Foreign keys explicitly indexed

### Recreate Database (Development)
```
rm data/secure_backend.db
alembic upgrade head
```

---

## 🧪 Development Workflow

### Run Application
```
uvicorn app.main:app --reload
```

### Run Tests
```
pytest -q
```

---

## 📌 Milestones

### ✅ Phase 1 — Authentication (Completed)
- [x] User model
- [x] Password hashing
- [x] Access token
- [x] Refresh token model
- [x] Alembic migrations
- [x] Database sync
- [x] Test suite green

### 🚧 Phase 2 — Multi-Tenant Architecture (In Progress)
- [x] Tenant model
- [x] Role model
- [x] UserRoles
- [x] Tenant-aware refresh tokens
- [x] Architecture stabilization
- [x] Error handling strategy
- [ ] Permission enforcement layer
- [ ] Tenant-scoped queries everywhere
- [ ] Role-based access in routers
- [ ] Admin endpoints

---

## 🧠 Design Philosophy

- Tenant isolation by design
- Deny-by-default access policy
- Explicit permission boundaries
- No implicit access
- Architecture-first development

---

## 📚 Documentation

- `docs/error-handling.md` — Official error-handling strategy
- `docs/tenant-isolation.md` — Tenant isolation rules & checklist
- `docs/architecture.md` — Layer boundaries & design (planned)

---

## 🚀 Vision

This backend is a **reference architecture** for secure, multi-tenant SaaS systems.
Every decision is intentional.