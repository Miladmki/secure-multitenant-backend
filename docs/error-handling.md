# Error Handling Strategy

This document defines the **official error-handling policy** for the Secure Multi-Tenant Backend project.
The goal is to ensure **consistent, predictable, and secure** API responses across the system.

---

## 🎯 Design Principles

- **Clarity**: Each HTTP status code has a single, well-defined meaning.
- **Security**: Error responses must not leak sensitive information.
- **Consistency**: The same class of error always maps to the same status code.
- **Deny-by-default**: Access is denied unless explicitly allowed.

---

## 📌 HTTP Status Code Policy

### 🔐 401 — Authentication Error

**When to use:**
- Missing access token
- Invalid or expired JWT
- Malformed Authorization header

**Characteristics:**
- The user identity is unknown or untrusted.
- No assumptions about roles or tenants are made.

**Example:**
```json
{
  "detail": "Not authenticated"
}
```

**Rules:**
- Returned only by authentication dependencies.
- Never used for permission or tenant issues.

---

### 🚫 403 — Authorization / Tenant / Role Error

**When to use:**
- User lacks required role
- Cross-tenant access attempt
- Access to a resource not permitted for the user

**Characteristics:**
- User is authenticated.
- User is identified, but access is forbidden.

**Example:**
```json
{
  "detail": "Not enough permissions"
}
```

**Rules:**
- Used for role-based access control.
- Used for tenant isolation enforcement.
- Must not reveal which permission or tenant caused the failure.

---

### 🔍 404 — Resource Not Found

**When to use:**
- Resource does not exist within the allowed scope.
- Resource exists globally but not within the user's tenant.

**Important Rule:**
> **404 is not a permission error.**  
> It is used to avoid leaking the existence of resources.

**Example:**
```json
{
  "detail": "Resource not found"
}
```

**Rules:**
- Preferred over 403 when resource existence must be hidden.
- Used after tenant filtering is applied.

---

### ⚠️ 400 — Validation / Business Rule Error

**When to use:**
- Invalid request payload
- Business rule violation
- Domain-specific constraints

**Characteristics:**
- Request is syntactically valid but semantically invalid.

**Example:**
```json
{
  "detail": "Email already registered"
}
```

**Rules:**
- Must provide actionable but non-sensitive feedback.
- Should not expose internal validation logic.

---

## 🧱 Enforcement Guidelines

- Authentication logic returns **401 only**.
- Authorization and tenant checks return **403 only**.
- Resource lookup after tenant filtering may return **404**.
- Validation and business logic errors return **400**.
- No endpoint should return ambiguous or overloaded status codes.

---

## ✅ Correct vs ❌ Incorrect Usage

| Scenario | Correct | Incorrect |
|-------|--------|----------|
| Missing token | 401 | 403 |
| Wrong role | 403 | 401 |
| Cross-tenant access | 403 | 404 |
| Hidden resource | 404 | 403 |
| Duplicate email | 400 | 409 |
| Validation error | 400 | 422 |

---

## 🏁 Summary

This strategy ensures:
- Strong security guarantees
- Predictable client behavior
- Clean separation of concerns
- Production-grade API semantics

All future endpoints and services **must comply** with this policy.