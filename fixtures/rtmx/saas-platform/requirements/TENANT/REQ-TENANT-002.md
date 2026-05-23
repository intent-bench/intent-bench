# REQ-TENANT-002: Organization CRUD

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement full CRUD operations for organizations with tenant isolation. Users can only view and manage organizations they belong to. Organization updates are restricted to owners and admins, and deletion is restricted to owners only. Deletion requires a confirmation mechanism to prevent accidental removal.

## Acceptance Criteria

1. GET /orgs/:slug returns organization details for members of that organization.
2. GET /orgs/:slug returns 404 Not Found for users who are not members of the organization.
3. PUT /orgs/:slug updates organization name; only owners and admins can update.
4. PUT /orgs/:slug by a member or viewer returns 403 Forbidden.
5. DELETE /orgs/:slug deletes the organization; only the owner can delete.
6. DELETE /orgs/:slug by a non-owner returns 403 Forbidden.
7. The slug cannot be changed after creation; attempts to update it are ignored or return an error.
8. A successful update returns 200 OK with the updated organization details.
9. A successful deletion returns 204 No Content and removes the organization and all associated data.
10. GET /orgs/:slug for a non-existent slug returns 404 Not Found.
11. All organization queries are scoped to the authenticated user's memberships; no cross-tenant data leakage.

## API Endpoints

### GET /orgs/:slug

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "starter",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-02-01T12:00:00Z"
}
```

### PUT /orgs/:slug

**Request:**
```json
{
  "name": "Acme Corporation"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "plan": "starter",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-02-10T09:00:00Z"
}
```

### DELETE /orgs/:slug

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "only the organization owner can delete the organization"
}
```

## Dependencies

- REQ-TENANT-001: Requires organization creation and membership to exist.
