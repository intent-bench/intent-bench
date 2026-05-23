# REQ-PROJ-001: Project CRUD

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement CRUD operations for projects within an organization. Projects are organizational units for grouping resources and are scoped to a single organization. Owners, admins, and members can create and update projects, while viewers can only read them. All project queries must enforce tenant isolation via org_id.

## Acceptance Criteria

1. POST /orgs/:slug/projects creates a new project within the organization.
2. Only owners, admins, and members can create projects; viewers receive 403 Forbidden.
3. GET /orgs/:slug/projects lists all non-archived projects in the organization (default behavior).
4. GET /orgs/:slug/projects?archived=true includes archived projects in the listing.
5. GET /orgs/:slug/projects/:id returns the details of a specific project.
6. PUT /orgs/:slug/projects/:id updates the project name and/or description.
7. Only owners, admins, and members can update projects; viewers receive 403 Forbidden.
8. A successful creation returns 201 Created with id, org_id, name, description, is_archived, and created_at.
9. Project names within an organization do not need to be unique.
10. Listing supports pagination with default 20 and max 100 per page.
11. Projects from other organizations are never returned (tenant isolation).

## API Endpoints

### POST /orgs/:slug/projects

**Request:**
```json
{
  "name": "Website Redesign",
  "description": "Q2 website overhaul project"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": false,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-01T10:00:00Z"
}
```

### GET /orgs/:slug/projects

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "org_id": 1,
    "name": "Website Redesign",
    "description": "Q2 website overhaul project",
    "is_archived": false,
    "created_at": "2026-02-01T10:00:00Z",
    "updated_at": "2026-02-01T10:00:00Z"
  }
]
```

### PUT /orgs/:slug/projects/:id

**Request:**
```json
{
  "name": "Website Redesign v2",
  "description": "Updated scope for Q3"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign v2",
  "description": "Updated scope for Q3",
  "is_archived": false,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-03-15T14:00:00Z"
}
```

## Dependencies

- REQ-RBAC-002: Requires RBAC middleware to enforce role-based permissions on project operations.
