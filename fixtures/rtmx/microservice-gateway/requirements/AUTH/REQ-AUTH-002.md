# REQ-AUTH-002: Authentication Middleware

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement API key authentication middleware that validates the X-API-Key header on all proxy requests and admin API endpoints. The middleware must hash the provided key, look it up in the database, verify it is active, and enforce role-based access control. Admin endpoints require the admin role; proxy endpoints accept either role.

## Acceptance Criteria

1. All proxy requests require an X-API-Key header; missing header returns 401 with a JSON error body.
2. An invalid API key (no matching hash in the database) returns 401.
3. A revoked API key (is_active = 0) returns 403 with a JSON error body indicating the key has been revoked.
4. A service-role key attempting to access /admin/* endpoints returns 403 with an insufficient permissions error.
5. An admin-role key can access both /admin/* endpoints and proxy endpoints.
6. A service-role key can access proxy endpoints.
7. The GET /health endpoint does not require authentication.
8. The authenticated key's id and role are attached to the request context for downstream middleware.
9. Key lookup uses the same hash algorithm as key creation (SHA-256 or bcrypt).
10. The middleware runs before rate limiting and all other middleware in the chain.

## API Endpoints

### Unauthenticated request

Request:
```
GET /api/users/123 HTTP/1.1
```

Response (401):
```json
{
  "error": "missing or invalid API key"
}
```

### Revoked key

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_revoked_key
```

Response (403):
```json
{
  "error": "API key has been revoked"
}
```

### Insufficient role

Request:
```
GET /admin/services HTTP/1.1
X-API-Key: sk_service_key
```

Response (403):
```json
{
  "error": "insufficient permissions: admin role required"
}
```

## Dependencies

- REQ-AUTH-001: API keys must be created before authentication can validate them.
