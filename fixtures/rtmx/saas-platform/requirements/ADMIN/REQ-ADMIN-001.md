# REQ-ADMIN-001: Platform Admin Organization Management

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement platform administration endpoints that allow platform admins (users with is_platform_admin=true) to list all organizations with usage statistics, and to suspend or unsuspend organizations. Suspended organizations cannot be accessed by their members until unsuspended. These endpoints are restricted exclusively to platform administrators and are not scoped to any single organization.

## Acceptance Criteria

1. GET /admin/orgs returns a paginated list of all organizations on the platform with usage statistics.
2. Each organization in the list includes id, name, slug, plan, member_count, project_count, resource_count, is_suspended, and created_at.
3. GET /admin/orgs supports page, per_page, and plan query parameters for filtering.
4. PUT /admin/orgs/:slug/suspend suspends the specified organization, blocking member access.
5. PUT /admin/orgs/:slug/unsuspend restores access to a previously suspended organization.
6. PUT /admin/orgs/:slug/suspend returns 400 if the organization is already suspended.
7. PUT /admin/orgs/:slug/unsuspend returns 400 if the organization is not currently suspended.
8. All /admin/* endpoints return 403 if the authenticated user does not have is_platform_admin=true.
9. Suspended organizations return 403 with a descriptive message on any member-facing endpoint.
10. Suspension and unsuspension actions are recorded in the audit log.

## API Endpoints

### GET /admin/orgs

**Request:**
```
GET /admin/orgs?page=1&per_page=20&plan=business
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "organizations": [
    {
      "id": 1,
      "name": "Acme Corp",
      "slug": "acme",
      "plan": "business",
      "member_count": 25,
      "project_count": 18,
      "resource_count": 1200,
      "is_suspended": false,
      "created_at": "2025-06-01T00:00:00Z"
    },
    {
      "id": 3,
      "name": "Widget Inc",
      "slug": "widget",
      "plan": "business",
      "member_count": 12,
      "project_count": 8,
      "resource_count": 450,
      "is_suspended": false,
      "created_at": "2025-09-15T00:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
}
```

### PUT /admin/orgs/:slug/suspend

**Response (200 OK):**
```json
{
  "slug": "acme",
  "is_suspended": true,
  "suspended_at": "2026-01-15T10:30:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "platform admin access required"
}
```

## Dependencies

- REQ-TENANT-002: Requires organization CRUD to provide the organization entities being managed.
