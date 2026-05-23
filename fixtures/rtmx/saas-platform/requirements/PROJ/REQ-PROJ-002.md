# REQ-PROJ-002: Project Archival

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Implement project archival and restoration endpoints for lifecycle management. Archiving a project marks it and its resources as inactive without permanently deleting data. Only owners and admins can archive or unarchive projects. Archived projects are hidden from default listings but can be viewed with an explicit filter.

## Acceptance Criteria

1. POST /orgs/:slug/projects/:id/archive sets the project's is_archived flag to true.
2. POST /orgs/:slug/projects/:id/unarchive sets the project's is_archived flag to false.
3. Only owners and admins can archive or unarchive projects; members and viewers receive 403 Forbidden.
4. Archiving an already-archived project returns 400 Bad Request.
5. Unarchiving a non-archived project returns 400 Bad Request.
6. Archived projects are excluded from GET /orgs/:slug/projects by default.
7. Archived projects are included when GET /orgs/:slug/projects?archived=true is specified.
8. Resources within an archived project remain accessible for read operations but cannot be created or updated.
9. A successful archive or unarchive returns 200 OK with the updated project details.
10. The updated_at timestamp is refreshed on archive and unarchive operations.

## API Endpoints

### POST /orgs/:slug/projects/:id/archive

**Response (200 OK):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": true,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-04-01T09:00:00Z"
}
```

### POST /orgs/:slug/projects/:id/unarchive

**Response (200 OK):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": false,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-04-05T11:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions: member cannot archive projects"
}
```

## Dependencies

- REQ-PROJ-001: Requires project CRUD to exist before archival can be implemented.
