# REQ-PROJ-003: Project Deletion with Cascade

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Implement project deletion with cascading removal of all associated resources. Only owners and admins can delete projects. Deletion is permanent and removes the project along with all its resources, webhook delivery records referencing those resources, and related audit log context. This is a destructive operation that cannot be undone.

## Acceptance Criteria

1. DELETE /orgs/:slug/projects/:id permanently deletes the project.
2. All resources belonging to the deleted project are permanently removed.
3. Only owners and admins can delete projects; members and viewers receive 403 Forbidden.
4. A successful deletion returns 204 No Content.
5. Deleting a non-existent project returns 404 Not Found.
6. Deleting a project in another organization returns 404 Not Found (tenant isolation).
7. An audit log entry is created for the deletion before the project is removed.
8. Webhook events (project.deleted) are fired before the project data is removed.
9. The deletion cascades atomically; if any part fails, the entire operation rolls back.
10. Archived projects can also be deleted.

## API Endpoints

### DELETE /orgs/:slug/projects/:id

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions: member cannot delete projects"
}
```

**Error (404 Not Found):**
```json
{
  "error": "project not found"
}
```

## Dependencies

- REQ-PROJ-002: Requires project archival to be in place as the non-destructive alternative.
