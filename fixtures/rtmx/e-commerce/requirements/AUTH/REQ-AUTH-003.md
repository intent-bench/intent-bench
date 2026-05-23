# REQ-AUTH-003: User Profile

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement endpoints to retrieve and update the authenticated user's profile. Users can view their full profile and update their username and email. Users cannot change their own role via the profile endpoint. Updates that would create duplicate email or username values must be rejected.

## Acceptance Criteria

1. GET /auth/profile returns the authenticated user's id, username, email, role, and created_at.
2. PUT /auth/profile updates the user's username and/or email.
3. PUT /auth/profile ignores any attempt to change the role field.
4. PUT /auth/profile with a duplicate email returns 409 Conflict.
5. PUT /auth/profile with a duplicate username returns 409 Conflict.
6. The updated_at timestamp is set automatically on profile update.
7. GET /auth/profile returns 401 Unauthorized when no valid token is provided.
8. A successful update returns 200 OK with the updated user record.

## API Endpoints

### GET /auth/profile

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "role": "customer",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
}
```

### PUT /auth/profile

**Request:**
```json
{
  "username": "alice_updated",
  "email": "alice_new@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice_updated",
  "email": "alice_new@example.com",
  "role": "customer",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-16T08:00:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already in use"
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication to identify the current user.
