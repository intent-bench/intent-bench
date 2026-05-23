# REQ-RES-001: Resource CRUD

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement CRUD operations for resources within projects. Resources are the core managed entities of the platform, each having a name, type, metadata (JSON), and status. Resources are scoped to a project within an organization. Deletion is a soft delete that changes the status to "deleted" rather than removing the record.

## Acceptance Criteria

1. POST /orgs/:slug/projects/:id/resources creates a new resource within the specified project.
2. Only owners, admins, and members can create resources; viewers receive 403 Forbidden.
3. GET /orgs/:slug/projects/:id/resources lists all active resources in the project.
4. GET /orgs/:slug/resources/:id returns the details of a specific resource.
5. PUT /orgs/:slug/resources/:id updates the resource name, type, metadata, or status.
6. DELETE /orgs/:slug/resources/:id performs a soft delete by setting status to "deleted".
7. A successful creation returns 201 Created with id, project_id, name, type, metadata, status, and created_at.
8. Resources are created with a default status of "active".
9. The metadata field accepts arbitrary JSON and stores it as-is.
10. Resources from archived projects cannot be created or updated; attempts return 400 Bad Request.
11. Soft-deleted resources are excluded from default listings.
12. Tenant isolation is enforced; resources from other organizations return 404 Not Found.

## API Endpoints

### POST /orgs/:slug/projects/:id/resources

**Request:**
```json
{
  "name": "Production Database",
  "type": "database",
  "metadata": {
    "engine": "postgresql",
    "version": "15",
    "region": "us-east-1"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Production Database",
  "type": "database",
  "metadata": {
    "engine": "postgresql",
    "version": "15",
    "region": "us-east-1"
  },
  "status": "active",
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-15T10:00:00Z"
}
```

### PUT /orgs/:slug/resources/:id

**Request:**
```json
{
  "name": "Production DB (Primary)",
  "metadata": {
    "engine": "postgresql",
    "version": "16",
    "region": "us-east-1"
  }
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Production DB (Primary)",
  "type": "database",
  "metadata": {
    "engine": "postgresql",
    "version": "16",
    "region": "us-east-1"
  },
  "status": "active",
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-03-01T08:00:00Z"
}
```

### DELETE /orgs/:slug/resources/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Production DB (Primary)",
  "type": "database",
  "status": "deleted",
  "updated_at": "2026-03-10T16:00:00Z"
}
```

## Dependencies

- REQ-PROJ-001: Requires project CRUD so that resources can be created within projects.
