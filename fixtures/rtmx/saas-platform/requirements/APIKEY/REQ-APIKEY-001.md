# REQ-APIKEY-001: API Key CRUD

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement API key creation, listing, and revocation for organizations. API keys provide programmatic access for integrations and automation. Only owners and admins can manage API keys. The full key value is returned only once at creation time; subsequent listings show only the prefix (first 8 characters). Keys are stored as hashes, never in plaintext.

## Acceptance Criteria

1. POST /orgs/:slug/api-keys creates a new API key and returns the full key value exactly once.
2. The API key is stored as a hash (bcrypt or SHA-256); the plaintext key is never stored in the database.
3. Only owners and admins can create API keys; members and viewers receive 403 Forbidden.
4. The response at creation includes the full key, id, name, prefix, scopes, and created_at.
5. GET /orgs/:slug/api-keys lists all API keys for the organization, showing prefix (first 8 chars) but never the full key.
6. DELETE /orgs/:slug/api-keys/:id revokes an API key, making it permanently unusable.
7. Only owners and admins can revoke API keys.
8. The key supports configurable scopes: read, write, admin.
9. A successful creation returns 201 Created.
10. A successful revocation returns 204 No Content.
11. API keys can have an optional expiration date; expired keys are rejected during authentication.
12. Creating an API key records the creating user's ID in the created_by field.

## API Endpoints

### POST /orgs/:slug/api-keys

**Request:**
```json
{
  "name": "CI/CD Pipeline",
  "scopes": ["read", "write"],
  "expires_at": "2027-01-01T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "CI/CD Pipeline",
  "key": "rtmx_k8f9a2b1c3d4e5f6g7h8i9j0k1l2m3n4",
  "prefix": "rtmx_k8f",
  "scopes": ["read", "write"],
  "expires_at": "2027-01-01T00:00:00Z",
  "created_by": 1,
  "created_at": "2026-02-15T10:00:00Z"
}
```

### GET /orgs/:slug/api-keys

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "CI/CD Pipeline",
    "prefix": "rtmx_k8f",
    "scopes": ["read", "write"],
    "last_used_at": "2026-03-01T12:00:00Z",
    "expires_at": "2027-01-01T00:00:00Z",
    "created_by": 1,
    "created_at": "2026-02-15T10:00:00Z"
  }
]
```

### DELETE /orgs/:slug/api-keys/:id

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions: member cannot manage API keys"
}
```

## Dependencies

- REQ-RBAC-002: Requires RBAC middleware to enforce that only owners and admins can manage API keys.
