# REQ-AUTH-001: API Key Management

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement admin endpoints for creating, listing, and revoking API keys. Each key has a role of either admin or service. The raw key value is returned only once at creation time; only the hash is stored. Admin keys grant access to admin endpoints and proxy, while service keys grant proxy access only.

## Acceptance Criteria

1. POST /admin/keys creates a new API key with name and role (admin or service).
2. POST /admin/keys returns 201 with the generated key value, id, name, and role.
3. The raw API key is returned only in the POST response and never again.
4. The key is stored as a cryptographic hash (SHA-256 or bcrypt) in the api_keys table.
5. GET /admin/keys returns 200 with an array of all keys showing id, name, role, is_active, and created_at but not the key value or hash.
6. DELETE /admin/keys/:id sets is_active to 0 (soft delete) and returns 204.
7. DELETE /admin/keys/:id returns 404 when the key id does not exist.
8. Creating a key with an invalid role (not admin or service) returns 422.
9. An optional rate_limit_override field sets a per-key rate limit that overrides the global default.
10. Creating a key without a required field (name, role) returns 422 with a descriptive error.

## API Endpoints

### POST /admin/keys

Request:
```json
{
  "name": "ci-pipeline",
  "role": "service",
  "rate_limit_override": 200
}
```

Response (201):
```json
{
  "id": 1,
  "key": "sk_live_a1b2c3d4e5f6g7h8i9j0",
  "name": "ci-pipeline",
  "role": "service",
  "rate_limit_override": 200,
  "is_active": true,
  "created_at": "2026-01-15T10:40:00Z"
}
```

### GET /admin/keys

Response (200):
```json
[
  {
    "id": 1,
    "name": "ci-pipeline",
    "role": "service",
    "rate_limit_override": 200,
    "is_active": true,
    "created_at": "2026-01-15T10:40:00Z"
  }
]
```

### DELETE /admin/keys/:id

Response (204): No content.

## Dependencies

- REQ-ROUTE-001: Routes must exist so that keys can be used to access them.
