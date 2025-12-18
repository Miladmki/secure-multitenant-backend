# Tenant Isolation Policy

## Secure Multi-Tenant Backend  
**Document Type:** Security & Architecture Policy  
**Status:** Active / Enforced  
**Applies To:** All backend services, APIs, and database access layers

---

## 1. Purpose

The purpose of this document is to define and enforce **strict tenant isolation rules**
across the entire backend system.

Tenant isolation ensures that:
- No user can access data belonging to another tenant
- No endpoint can accidentally leak cross-tenant data
- Security is enforced **by design**, not by convention

This policy is mandatory for all current and future development.

---

## 2. Core Principles

### 2.1 Isolation by Default
- All data access is tenant-scoped by default
- Cross-tenant access is **denied unless explicitly designed and reviewed**

### 2.2 Trust Boundary
- Tenant identity is derived **only** from authenticated user context
- Tenant information must **never** be accepted directly from client input

### 2.3 Defense in Depth
Tenant isolation must be enforced at:
- Dependency layer
- Query layer
- Authorization layer
- Test coverage layer

Failure in one layer must not compromise isolation.

---

## 3. Tenant Source of Truth

### Allowed Sources
Tenant identity may be derived **only** from:
- `current_user.tenant_id`
- JWT claims populated at login (validated server-side)

### Forbidden Sources
Tenant identity must **never** be derived from:
- Request body
- Query parameters
- Path parameters
- Frontend-provided tenant IDs

**Rationale:** Prevent tenant spoofing and privilege escalation.

---

## 4. Data Model Rules

### 4.1 Tenant-Scoped Tables
All tenant-specific tables **must** include:

```
tenant_id (FK → tenants.id)
```

### 4.2 Global Tables
Global tables (rare) must be:
- Explicitly documented
- Reviewed for security implications

---

## 5. Query-Level Enforcement

### 5.1 Mandatory Query Pattern

All queries for tenant-scoped entities **must** include tenant filtering:

```python
db.query(Entity).filter(
    Entity.tenant_id == current_tenant.id
)
```

### 5.2 Forbidden Query Patterns ❌

```python
db.query(Entity).all()
db.query(Entity).filter(Entity.id == some_id)
db.get(Entity, id)
```

Unless tenant scoping is explicitly applied.

---

## 6. Dependency Enforcement

### Required Dependencies

Endpoints accessing tenant-scoped data **must** use:

- `get_current_user`
- `get_current_tenant`

### Validation Rules
- If user has no tenant → `403 Forbidden`
- If tenant mismatch detected → `403 Forbidden`

---

## 7. Role & Tenant Interaction

### Key Rule
Roles **do not override tenant boundaries**.

| Scenario                     | Result    |
| ---------------------------- | --------- |
| Admin accessing own tenant   | Allowed   |
| Admin accessing other tenant | Forbidden |
| User accessing other tenant  | Forbidden |

There is **no cross-tenant admin** unless explicitly designed.

---

## 8. API Design Rules

### Allowed
- `/resources` → tenant inferred from user
- `/me` → current user only

### Forbidden ❌
- `/tenants/{tenant_id}/resources`
- `/resources?tenant_id=...`

Tenant context must never be client-controlled.

---

## 9. Testing Requirements

### Mandatory Test Coverage
For every tenant-scoped endpoint, tests **must include**:

- User in correct tenant → 200
- User in different tenant → 403
- User without tenant → 403
- Admin role + wrong tenant → 403

---

## 10. Security Checklist (Before Merge)

- [ ] No tenant_id accepted from client input
- [ ] All queries are tenant-scoped
- [ ] `get_current_tenant` is enforced
- [ ] Role checks do not bypass tenant isolation
- [ ] Tests cover cross-tenant denial cases
- [ ] No `.all()` or unfiltered queries on tenant tables

---

## 11. Violation Severity

Tenant isolation violations are classified as **Critical Security Bugs**.

---

## 12. Summary

Tenant isolation is a **non-negotiable security boundary**.