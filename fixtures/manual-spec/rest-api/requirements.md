# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-API-001: GET /health returns 200 without authentication

**Phase:** 1

*Monitoring endpoint*

### Acceptance Criteria

- Returns 200 with `{"status": "ok"}`
- No authentication required

---

## 2. REQ-AUTH-001: POST /auth/register creates user with hashed password and default viewer role

**Phase:** 1

*Foundation: user creation*

### Acceptance Criteria

- Accepts username, email, password in request body
- Password is hashed before storage (bcrypt or argon2)
- Default role is "viewer"
- Returns 201 with user object (id, username, email, role, created_at)
- Password hash is never returned in any response
- Duplicate username or email returns 409

---

## 3. REQ-AUTH-002: POST /auth/login returns JWT token for valid credentials

**Phase:** 1

**Depends on:** REQ-AUTH-001

*Foundation: token issuance*

### Acceptance Criteria

- Accepts username and password
- Returns 200 with `token` field containing a valid JWT
- JWT payload includes user id and role
- Invalid credentials return 401
- Token is signed with a server secret

---

## 4. REQ-AUTH-005: Missing or invalid tokens return 401

**Phase:** 1

**Depends on:** REQ-AUTH-002

*Security foundation*

### Acceptance Criteria

- No Authorization header: 401
- Malformed token: 401
- Expired token: 401
- Applies to all endpoints except /health and /auth/register and /auth/login

---

## 5. REQ-RBAC-001: Users have roles: admin staff viewer

**Phase:** 1

**Depends on:** REQ-AUTH-001

*Foundation for access control*

### Acceptance Criteria

- Three valid roles: admin, staff, viewer
- Role is stored with the user record
- Role is included in JWT payload
- Default role on registration is viewer

---

## 6. REQ-AUTH-003: GET /auth/me returns authenticated user profile

**Phase:** 2

**Depends on:** REQ-AUTH-001, REQ-AUTH-002

*Requires valid token*

### Acceptance Criteria

- Requires valid JWT in Authorization header (Bearer scheme)
- Returns 200 with user object (id, username, email, role)
- Returns 401 if token is missing or invalid

---

## 7. REQ-AUTH-004: JWT tokens expire after 1 hour

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Security requirement*

### Acceptance Criteria

- Token `exp` claim is set to 1 hour from issuance
- Expired tokens return 401

---

## 8. REQ-BOOK-001: GET /books returns paginated list with default 20 per page max 100

**Phase:** 2

**Depends on:** REQ-AUTH-002, REQ-AUTH-005

*Requires auth middleware*

### Acceptance Criteria

- Query params: `page` (default 1), `per_page` (default 20, max 100)
- Response includes book array and total count
- Per_page > 100 is clamped to 100
- Returns 200 with empty array when no books exist

---

## 9. REQ-BOOK-002: GET POST PUT DELETE /books with proper status codes

**Phase:** 2

**Depends on:** REQ-BOOK-001

*Core data operations*

### Acceptance Criteria

- POST /books: 201 with created book (title, author, isbn, price, stock_quantity required)
- GET /books/:id: 200 with book object
- PUT /books/:id: 200 with updated book
- DELETE /books/:id: 204 no content

---

## 10. REQ-API-002: Missing resources return 404

**Phase:** 2

**Depends on:** REQ-BOOK-002

*Error handling*

### Acceptance Criteria

- GET /books/:id with nonexistent id returns 404
- PUT /books/:id with nonexistent id returns 404
- DELETE /books/:id with nonexistent id returns 404

---

## 11. REQ-BOOK-003: ISBN must be unique and valid 10 or 13 digits with 422 on invalid

**Phase:** 3

**Depends on:** REQ-BOOK-002

*Data integrity*

### Acceptance Criteria

- ISBN validated: must be exactly 10 or 13 digits
- Duplicate ISBN returns 409 or 422
- Missing required fields return 422 with field names
- Price must be non-negative
- Stock quantity must be non-negative integer

---

## 12. REQ-RBAC-002: Create/update books requires admin or staff and delete requires admin only

**Phase:** 3

**Depends on:** REQ-RBAC-001, REQ-BOOK-002

*Cross-cutting: auth x books*

### Acceptance Criteria

- POST /books: 403 for viewer role
- PUT /books/:id: 403 for viewer role
- DELETE /books/:id: 403 for staff and viewer roles
- GET /books and GET /books/:id: allowed for all authenticated roles

---

## 13. REQ-RBAC-003: GET /users and PUT /users/:id/role require admin role

**Phase:** 3

**Depends on:** REQ-RBAC-001, REQ-AUTH-003

*Admin-only management*

### Acceptance Criteria

- GET /users: returns user list for admin, 403 for others
- PUT /users/:id/role: updates role for admin, 403 for others
- Role can be changed to any valid role

---
