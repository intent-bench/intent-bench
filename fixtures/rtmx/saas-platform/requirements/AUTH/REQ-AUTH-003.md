# REQ-AUTH-003: User Profile

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement endpoints for authenticated users to view and update their own profile information. Users can update their username and email but cannot change their role or admin status through this endpoint. The password hash must never be included in profile responses.

## Acceptance Criteria

1. GET /auth/me returns the authenticated user's profile (id, username, email, is_platform_admin, created_at, updated_at).
2. PUT /auth/me updates the authenticated user's username and/or email.
3. The password_hash is never included in any profile response.
4. Updating to a username that is already taken returns 409 Conflict.
5. Updating to an email that is already taken returns 409 Conflict.
6. The updated_at timestamp is refreshed on successful update.
7. A successful update returns 200 OK with the full updated profile.
8. Unauthenticated requests return 401 Unauthorized.
9. PUT /auth/me with no valid fields to update returns 400 Bad Request.
10. Users cannot modify is_platform_admin through this endpoint; attempts to set it are ignored.

## API Endpoints

### GET /auth/me

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### PUT /auth/me

**Request:**
```json
{
  "username": "alice_updated",
  "email": "alice.new@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice_updated",
  "email": "alice.new@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-16T08:00:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already registered"
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication middleware to identify the current user.
