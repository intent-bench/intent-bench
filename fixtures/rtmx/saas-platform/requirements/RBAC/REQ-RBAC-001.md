# REQ-RBAC-001: Role Assignment

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement a role-based access control system with four roles: owner, admin, member, and viewer. Each organization member has exactly one role that determines their permissions within that organization. Role assignment occurs at membership creation (owner on org creation, specified role on invitation acceptance) and can be changed by owners and admins.

## Acceptance Criteria

1. The system supports four roles: owner, admin, member, and viewer, with a clear permission hierarchy.
2. Organization creators are automatically assigned the "owner" role.
3. Invited users are assigned the role specified in the invitation upon acceptance.
4. PUT /orgs/:slug/members/:user_id/role changes a member's role.
5. Only owners and admins can change member roles.
6. An admin cannot promote a member to owner or change another admin's role.
7. An owner can assign any role including owner (transferring ownership).
8. The last owner of an organization cannot have their role changed; the request returns 400 Bad Request.
9. Changing a role to an invalid value returns 422 Unprocessable Entity.
10. A successful role change returns 200 OK with the updated membership details.
11. Attempting to change the role of a non-member returns 404 Not Found.

## API Endpoints

### PUT /orgs/:slug/members/:user_id/role

**Request:**
```json
{
  "role": "admin"
}
```

**Response (200 OK):**
```json
{
  "user_id": 2,
  "org_id": 1,
  "role": "admin",
  "joined_at": "2026-01-20T14:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions to change roles"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "cannot remove the last owner of the organization"
}
```

## Dependencies

- REQ-TENANT-001: Requires organization creation with owner membership.
