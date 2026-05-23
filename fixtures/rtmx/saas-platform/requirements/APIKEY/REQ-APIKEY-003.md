# REQ-APIKEY-003: API Key Scope Enforcement

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement scope enforcement for API key authenticated requests. Each API key has a set of scopes (read, write, admin) that determine which operations the key can perform. The scope check runs after API key authentication and before the request reaches the handler. Operations that exceed the key's scopes are rejected with 403 Forbidden.

## Acceptance Criteria

1. API keys with "read" scope can perform GET requests on org-scoped endpoints.
2. API keys with "write" scope can perform GET, POST, PUT, and DELETE requests on resource and project endpoints.
3. API keys with "admin" scope can perform all operations including member management, API key management, and webhook management.
4. A "read" scope key attempting a POST returns 403 Forbidden.
5. A "write" scope key attempting to manage members or API keys returns 403 Forbidden.
6. Scope enforcement is checked after API key authentication succeeds.
7. The error response includes which scope is required for the attempted operation.
8. An API key with multiple scopes has the union of all permissions from those scopes.
9. An API key with no scopes can only authenticate but cannot access any endpoints (returns 403 for all operations).
10. Scope enforcement does not apply to JWT-authenticated requests (JWT uses RBAC roles instead).

## API Endpoints

Scope enforcement is a cross-cutting middleware, not a standalone endpoint.

### Example: Read-Only Key Attempting a Write

**Request:**
```
POST /orgs/acme-corp/projects
X-API-Key: rtmx_readonly_key_value
```
```json
{
  "name": "New Project"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "API key scope 'write' required for this operation"
}
```

### Example: Write Key Attempting Admin Operation

**Request:**
```
POST /orgs/acme-corp/api-keys
X-API-Key: rtmx_write_key_value
```
```json
{
  "name": "Another Key",
  "scopes": ["read"]
}
```

**Response (403 Forbidden):**
```json
{
  "error": "API key scope 'admin' required for this operation"
}
```

## Dependencies

- REQ-APIKEY-002: Requires API key authentication middleware to resolve the key and its scopes.
