# REQ-RBAC-003: Admin Endpoints

## Requirement
GET /users and PUT /users/:id/role require admin role.

## Acceptance Criteria
- GET /users: returns user list for admin, 403 for others
- PUT /users/:id/role: updates role for admin, 403 for others
- Role can be changed to any valid role

## Dependencies
- REQ-RBAC-001, REQ-AUTH-003

## Test
`TestAdminEndpoints` in test module
