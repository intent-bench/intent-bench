# REQ-AUTH-002: JWT Authentication

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Implement a login endpoint that authenticates users with email and password, returning a signed JWT with a one-hour expiry on success. Implement authentication middleware that extracts the user identity from the JWT on protected routes and rejects requests with missing, invalid, or expired tokens with 401 Unauthorized.

## Acceptance Criteria

1. POST /auth/login with valid credentials returns a signed JWT in the response body.
2. POST /auth/login with an invalid email returns 401 Unauthorized.
3. POST /auth/login with a valid email but incorrect password returns 401 Unauthorized.
4. The JWT payload contains at minimum: user_id, username, role, and an expiration claim (exp) set to 1 hour from issuance.
5. The authentication middleware extracts the user from a valid JWT in the Authorization header (Bearer scheme).
6. The middleware returns 401 Unauthorized when no Authorization header is present.
7. The middleware returns 401 Unauthorized when the JWT is expired or has an invalid signature.
8. All routes except POST /auth/register and POST /auth/login are protected by the middleware.
9. The user's role from the JWT is available to downstream handlers for authorization checks.

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
    "role": "customer"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "invalid credentials"
}
```

## Dependencies

- REQ-AUTH-001: Requires user registration so credentials exist to authenticate against.
