# REQ-TENANT-001: Organization Creation with Owner Assignment

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement an endpoint for authenticated users to create new organizations. The creating user is automatically assigned as the organization owner via a membership record. Organization slugs must be unique and are used as the primary identifier in URL paths.

## Acceptance Criteria

1. POST /orgs creates a new organization and returns the organization details.
2. The authenticated user is automatically added as a member with the "owner" role.
3. The organization slug must be unique; duplicate slugs return 409 Conflict.
4. The organization is created with the default plan of "free".
5. A successful creation returns 201 Created with id, name, slug, plan, and created_at.
6. The slug must contain only lowercase letters, numbers, and hyphens; invalid slugs return 422 Unprocessable Entity.
7. The name and slug fields are required; missing fields return 400 Bad Request.
8. GET /orgs returns only organizations the authenticated user belongs to.
9. The membership record includes the user_id, org_id, role ("owner"), and joined_at timestamp.
10. Unauthenticated requests return 401 Unauthorized.

## API Endpoints

### POST /orgs

**Request:**
```json
{
  "name": "Acme Corp",
  "slug": "acme-corp"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "free",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "organization slug already exists"
}
```

### GET /orgs

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Acme Corp",
    "slug": "acme-corp",
    "plan": "free",
    "role": "owner",
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication middleware to identify the creating user.
