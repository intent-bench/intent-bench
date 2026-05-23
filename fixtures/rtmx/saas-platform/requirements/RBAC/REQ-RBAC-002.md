# REQ-RBAC-002: RBAC Middleware Enforcement

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement middleware that enforces role-based access control on every organization-scoped endpoint. The middleware must check the authenticated user's role within the target organization against the permission matrix before allowing the request to proceed. Insufficient permissions must return 403 Forbidden.

## Acceptance Criteria

1. The middleware checks the user's role in the target organization for every org-scoped request.
2. Owners and admins can manage org settings (PUT /orgs/:slug).
3. Owners and admins can manage members (invite, change role, remove).
4. Only owners can manage billing (PUT /orgs/:slug/billing/plan).
5. Owners, admins, and members can create and edit projects and resources.
6. Only owners and admins can archive and delete projects.
7. All roles (including viewer) can view projects and resources.
8. Only owners and admins can manage API keys and webhooks.
9. Only owners and admins can view the audit log.
10. A user with insufficient permissions receives 403 Forbidden with a descriptive error message.
11. The middleware runs after authentication and tenant isolation checks, ensuring the user is both authenticated and a member of the organization.
12. Platform admins bypass org-level RBAC checks for admin console endpoints only.

## API Endpoints

RBAC enforcement is a cross-cutting middleware applied to all org-scoped endpoints.

### Example: Viewer Attempting to Create a Project

**Request:**
```
POST /orgs/acme-corp/projects
Authorization: Bearer <jwt-for-viewer>
```
```json
{
  "name": "New Project",
  "description": "A project"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "insufficient permissions: viewer cannot create projects"
}
```

### Example: Member Attempting to Delete a Project

**Request:**
```
DELETE /orgs/acme-corp/projects/1
Authorization: Bearer <jwt-for-member>
```

**Response (403 Forbidden):**
```json
{
  "error": "insufficient permissions: member cannot delete projects"
}
```

## Dependencies

- REQ-RBAC-001: Requires role assignment to determine user permissions.
- REQ-TENANT-003: Requires tenant isolation to resolve org membership before checking roles.
