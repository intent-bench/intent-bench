# REQ-APIKEY-002: API Key Authentication Middleware

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement authentication middleware that accepts API keys via the X-API-Key header as an alternative to JWT bearer tokens. When an API key is provided, the middleware must validate the key by hashing it and comparing against stored hashes, resolve the associated organization, and attach the org context to the request. API key authentication skips user-level context but enforces organization-level scoping.

## Acceptance Criteria

1. The middleware accepts an X-API-Key header on all org-scoped endpoints.
2. A valid API key authenticates the request and resolves the associated organization.
3. An invalid or revoked API key returns 401 Unauthorized.
4. An expired API key returns 401 Unauthorized with a message indicating expiration.
5. The middleware updates the last_used_at timestamp on successful authentication.
6. When both Authorization (JWT) and X-API-Key headers are provided, JWT takes precedence.
7. API key authentication sets the org context but does not set a user context (user_id is null in audit logs for API key requests).
8. The middleware identifies the key by matching the prefix, then validates by comparing the full key hash.
9. Requests without any authentication header to protected endpoints return 401 Unauthorized.
10. API key authentication enforces tenant isolation; the key can only access data within its associated organization.

## API Endpoints

API key authentication is a cross-cutting middleware, not a standalone endpoint.

### Example: Accessing Resources via API Key

**Request:**
```
GET /orgs/acme-corp/projects
X-API-Key: rtmx_k8f9a2b1c3d4e5f6g7h8i9j0k1l2m3n4
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "org_id": 1,
    "name": "Website Redesign",
    "description": "Q2 website overhaul project",
    "is_archived": false,
    "created_at": "2026-02-01T10:00:00Z"
  }
]
```

### Example: Invalid API Key

**Request:**
```
GET /orgs/acme-corp/projects
X-API-Key: rtmx_invalid_key_value
```

**Response (401 Unauthorized):**
```json
{
  "error": "invalid API key"
}
```

### Example: Expired API Key

**Response (401 Unauthorized):**
```json
{
  "error": "API key has expired"
}
```

## Dependencies

- REQ-APIKEY-001: Requires API key CRUD to create and store API keys for validation.
