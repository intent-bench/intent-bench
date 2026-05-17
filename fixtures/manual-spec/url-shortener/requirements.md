# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-STORE-001: Initialize SQLite database with urls table (id short_code original_url clicks created_at)

**Phase:** 1

*Foundation -- all API endpoints depend on storage*

---

## 2. REQ-STORE-002: Generate unique 6-8 character alphanumeric short codes

**Phase:** 1

**Depends on:** REQ-STORE-001

*Must be URL-safe: [a-zA-Z0-9]*

---

## 3. REQ-API-001: POST /shorten accepts JSON url and returns short_code and short_url

**Phase:** 2

**Depends on:** REQ-STORE-001, REQ-STORE-002

*Primary endpoint*

---

## 4. REQ-VALID-001: Reject non-URL input on POST /shorten with HTTP 400

**Phase:** 2

**Depends on:** REQ-API-001

*Must validate before storing*

---

## 5. REQ-VALID-002: Reject empty body on POST /shorten with HTTP 400

**Phase:** 2

**Depends on:** REQ-API-001

*Edge case*

---

## 6. REQ-API-002: GET /:code redirects to original URL with HTTP 301

**Phase:** 2

**Depends on:** REQ-STORE-001

*Must increment click counter*

---

## 7. REQ-API-003: GET /stats/:code returns JSON with short_code url and clicks

**Phase:** 2

**Depends on:** REQ-STORE-001, REQ-API-002

*Read-only endpoint*

---

## 8. REQ-VALID-003: Return HTTP 404 for unknown short codes on GET and stats

**Phase:** 2

**Depends on:** REQ-API-002, REQ-API-003

*Both /:code and /stats/:code*

---

## 9. REQ-RATE-001: Rate limit POST /shorten to 10 requests per minute per IP

**Phase:** 3

**Depends on:** REQ-API-001

*Per-IP tracking*

---

## 10. REQ-TEST-001: Comprehensive test suite runnable with single command

**Phase:** 3

**Depends on:** REQ-API-001, REQ-API-002, REQ-API-003, REQ-VALID-001, REQ-VALID-002, REQ-VALID-003, REQ-RATE-001

*All endpoints and edge cases covered*

---
