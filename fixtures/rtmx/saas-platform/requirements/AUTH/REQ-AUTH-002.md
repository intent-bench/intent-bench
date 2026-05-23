# REQ-AUTH-002: JWT Login and Authentication Middleware

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Implement a login endpoint that authenticates users with email and password, returning a signed JWT token. Implement authentication middleware that validates JWT tokens on all protected endpoints. Tokens must expire after 1 hour and include the user ID in the payload.

## Acceptance Criteria

1. POST /auth/login accepts email and password, returning a JWT token on success.
2. The JWT token includes the user's id in the payload and expires after 1 hour.
3. Invalid email or password returns 401 Unauthorized with a generic error message (no indication of which field is wrong).
4. The authentication middleware extracts the JWT from the Authorization header (Bearer scheme).
5. Requests without a valid Authorization header to protected endpoints return 401 Unauthorized.
6. Expired tokens return 401 Unauthorized with an appropriate error message.
7. Malformed or tampered tokens return 401 Unauthorized.
8. The middleware attaches the authenticated user's ID to the request context for downstream handlers.
9. Login with missing required fields (email, password) returns 400 Bad Request.
10. A successful login returns 200 OK with the token and user details (without password_hash).

## API Endpoints

### POST /auth/login

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "is_platform_admin": false
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "invalid email or password"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "email and password are required"
}
```

## Dependencies

- REQ-AUTH-001: Requires user registration to create accounts for login.
