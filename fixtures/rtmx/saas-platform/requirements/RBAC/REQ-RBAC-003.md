# REQ-RBAC-003: Member Management and Invitation Flow

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement member management and invitation workflows for organizations. Organization owners and admins can invite users by email, change member roles, and remove members. Invited users receive a unique token to accept the invitation and join the organization with the assigned role. The system must prevent removing the last owner of an organization.

## Acceptance Criteria

1. POST /orgs/:slug/invitations creates an invitation with a unique token, email, role, invited_by, and expires_at.
2. POST /orgs/:slug/invitations returns 403 if the authenticated user is not an owner or admin.
3. POST /orgs/:slug/invitations returns 409 if the email is already a member of the organization.
4. GET /orgs/:slug/invitations lists all pending (unaccepted, unexpired) invitations for the organization.
5. DELETE /orgs/:slug/invitations/:id cancels a pending invitation (owner/admin only).
6. POST /invitations/:token/accept adds the authenticated user to the organization with the invited role.
7. POST /invitations/:token/accept returns 404 for invalid or expired tokens.
8. PUT /orgs/:slug/members/:user_id/role changes a member's role (owner/admin only).
9. PUT /orgs/:slug/members/:user_id/role returns 403 if the authenticated user lacks permission.
10. DELETE /orgs/:slug/members/:user_id removes a member from the organization (owner/admin only).
11. DELETE /orgs/:slug/members/:user_id returns 400 if the target is the last owner of the organization.
12. All invitation and member management operations create audit log entries and trigger notifications.

## API Endpoints

### POST /orgs/:slug/invitations

**Request:**
```json
{
  "email": "bob@example.com",
  "role": "member"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "email": "bob@example.com",
  "role": "member",
  "token": "inv_abc123def456",
  "invited_by": 1,
  "expires_at": "2026-02-15T10:30:00Z",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "user is already a member of this organization"
}
```

### POST /invitations/:token/accept

**Response (200 OK):**
```json
{
  "org_id": 1,
  "user_id": 5,
  "role": "member",
  "joined_at": "2026-01-16T09:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "invitation not found or expired"
}
```

### DELETE /orgs/:slug/members/:user_id

**Response (204 No Content)**

**Error (400 Bad Request):**
```json
{
  "error": "cannot remove the last owner of the organization"
}
```

## Dependencies

- REQ-RBAC-002: Requires role-based access control middleware to enforce owner/admin permissions.
