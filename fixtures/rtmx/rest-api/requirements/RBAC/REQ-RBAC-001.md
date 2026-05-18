# REQ-RBAC-001: Role System

## Requirement
Users have roles: admin, staff, viewer.

## Acceptance Criteria
- Three valid roles: admin, staff, viewer
- Role is stored with the user record
- Role is included in JWT payload
- Default role on registration is viewer

## Dependencies
- REQ-AUTH-001

## Test
`TestUserRoles` in test module
