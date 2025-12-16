# Secure Multi-Tenant Backend

A **production-oriented FastAPI backend** focused on **secure authentication**, **token lifecycle management**, and **multi-tenant readiness**.

This project is intentionally built step-by-step with **real-world constraints**:
schema migrations, token rotation, test-driven fixes, and clean commits.

---

## Project Status

**Phase 1 – Authentication & Security Foundation (In Progress)**

Current focus:
- User authentication
- JWT access tokens
- Refresh token lifecycle
- Database schema stability via Alembic
- Automated tests (pytest)

---

## Core Objectives

### 1. Secure Authentication (Current Phase)
- Email + password login
- Strong password hashing (Argon2)
- JWT access tokens (short-lived)
- Refresh tokens (long-lived, revocable)
- Explicit token lifecycle (create, store, expire, revoke)

### 2. Database Stability
- SQLAlchemy ORM (Declarative Base)
- Alembic migrations for **every schema change**
- No manual schema edits
- SQLite for development/testing
- PostgreSQL planned for production

### 3. Test-Driven Backend
- Pytest-based integration tests
- Auth flows tested end-to-end
- Refresh token flow validated by tests
- Green test suite required before moving phases

### 4. Multi-Tenant Readiness (Next Phases)
- Tenant-aware user model
- Scoped access tokens
- Role-based authorization
- Tenant isolation at query level

---

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Password Hashing:** Argon2 (passlib)
- **Database (dev/test):** SQLite
- **Database (prod):** PostgreSQL (planned)
- **Testing:** Pytest
- **Containerization:** Docker (planned)

---

## Project Structure (Relevant Parts)

