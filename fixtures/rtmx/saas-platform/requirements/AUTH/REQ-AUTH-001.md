# REQ-AUTH-001: User Registration

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Implement a user registration endpoint that creates new user accounts with securely hashed passwords. Passwords must be hashed using bcrypt or argon2 before storage. The system must reject duplicate email addresses and duplicate usernames, and must never return the password hash in any response.

## Acceptance Criteria

1. POST /auth/register creates a new user and returns the user record without password_hash.
2. The password is hashed with bcrypt or argon2 before being stored in the database.
3. The plaintext password is never stored in the database or returned in any response.
4. New users have is_platform_admin set to false by default.
5. Attempting to register with a duplicate email returns 409 Conflict.
6. Attempting to register with a duplicate username returns 409 Conflict.
7. A successful registration returns 201 Created with the user's id, username, email, is_platform_admin, and created_at.
8. The created_at and updated_at timestamps are set automatically at registration time.
9. Registration with missing required fields (username, email, password) returns 400 Bad Request.
10. Email format is validated; invalid emails return 422 Unprocessable Entity.
11. Password must be at least 8 characters; shorter passwords return 422 Unprocessable Entity.

## API Endpoints

### POST /auth/register

**Request:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already registered"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "username, email, and password are required"
}
```

## Dependencies

- REQ-DB-001: Requires the users table to exist.
