# Architecture Notes

## Overview
This document describes the **current security and architecture design** of the Secure Multi-Tenant Backend.
It reflects the **implemented state** of the system and documents the reasoning behind key decisions.
Future extensions are listed explicitly and are not yet implemented.

---

## 1. Authentication Flow (JWT + Refresh Tokens)

### Access Token (JWT)
- **Stateless**
- Used for every authenticated API request
- Contains only minimal claims

#### Access Token Claims
| Claim | Description |
|------|-------------|
| sub | User ID |
| tenant_id | Tenant ID (mandatory for isolation) |

**Roles are intentionally NOT included** in the access token.

#### Why roles are not inside the token
- Roles may change during token lifetime
- Old tokens must not preserve outdated privileges
- Enforces role checks via database (stateful, authoritative)
- Stronger tenant isolation guarantees

### Refresh Token
- **Stateful**
- Stored in database
- Linked to:
  - User
  - Tenant
- Has expiration
- Can be revoked on logout

#### Refresh Token Policy
| Feature | Status |
|------|------|
| Stored in DB | Yes |
| User-bound | Yes |
| Tenant-bound | Yes |
| Rotation | No (planned) |
| Revocation | Yes |

#### Why refresh tokens are stateful
- Enables logout & revocation
- Allows tenant-aware validation
- Detects misuse
- Enforces expiration

#### Why access tokens are stateless
- High performance
- No DB lookup per request
- Suitable for high-frequency API calls

### Authentication Runtime Flow
```
Client
  → /login
    → access_token (JWT)
    → refresh_token (DB)

Request
  → access_token
    → get_current_user
    → get_current_tenant
    → role enforcement
    → endpoint
```

---

## 2. Role Enforcement Flow

### Role Model
- Role is a **simple string** (e.g. `admin`, `user`)
- Many-to-many relationship between users and roles
- Designed for future permission-based expansion

### Current Enforcement
- Implemented via dependency:
```python
require_role("admin")
```

### Deny-By-Default Policy
| Scenario | Result |
|--------|-------|
| Authenticated but no role | 403 |
| Missing role | 403 |
| Missing dependency | Security bug |
| Admin outside tenant | 403 |

### Why role checks live in dependencies
- Centralized enforcement
- Prevents bypass
- Keeps routers clean
- Improves testability
- Enforces consistency

### Runtime Role Enforcement Flow
```
access_token
  ↓
get_current_user
  ↓
get_current_tenant
  ↓
require_role
  ↓
endpoint
```

---

## 3. Tenant Isolation

### Tenant Resolution
- Tenant is resolved **only from the authenticated user**
- Not accepted from:
  - Headers
  - Query parameters
  - Subdomains

#### Why
- Prevents spoofing
- Simplifies architecture
- Strong security guarantees

### Enforcement Points

#### 1) Dependency Layer
- `get_current_user`
- `get_current_tenant`
- `require_role`

#### 2) Query Layer
Every query **must include tenant filtering**
```sql
WHERE tenant_id = current_tenant.id
```

#### 3) Router Layer
- No endpoint is allowed without tenant-aware dependencies
- Cross-tenant access is always forbidden

### Admin Scope
- Admins are **tenant-scoped**
- No super-admin exists at this stage

---

## 4. Deny-By-Default Philosophy

### Core Rules
- Every endpoint must declare security dependencies
- Missing dependency = **security bug**
- No implicit access, even for admins

### Error Semantics
| Status | Meaning |
|------|--------|
| 401 | Authentication failure |
| 403 | Authorization / tenant / role violation |
| 404 | Resource does not exist (not permission) |

#### Why 403 instead of 404
- Clear permission failure
- Better audit logs
- Avoids ambiguity
- Prevents security confusion

### Why deny-by-default scales
- Prevents privilege creep
- Centralized enforcement
- Easy to audit
- Easy to test
- Resistant to future complexity

---

## 5. Dependency Architecture

### deps.py Responsibilities
- `get_current_user`
- `get_current_tenant`
- `require_role`

### Why dependencies live in core
- Core = security layer
- Routers = API surface
- Prevents circular imports
- Enables unit testing without FastAPI
- Enforces clean architecture boundaries

---

## 6. Future Extensions (Not Implemented)

Planned but intentionally excluded from current implementation:
- Permission-based authorization
- Action-level permissions
- Resource-scoped permissions
- Super-admin role
- External identity providers (OIDC)
- Token rotation with chaining

These features must integrate without violating:
- Tenant isolation
- Deny-by-default
- Centralized enforcement

---

## Final Notes
This architecture favors **explicitness over convenience**.
Security is enforced centrally and intentionally.
No shortcut is considered acceptable if it weakens isolation guarantees.
