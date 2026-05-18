# REQ-RBAC-002: Book Access Control

## Requirement
Create/update books requires admin or staff; delete requires admin only.

## Acceptance Criteria
- POST /books: 403 for viewer role
- PUT /books/:id: 403 for viewer role
- DELETE /books/:id: 403 for staff and viewer roles
- GET /books and GET /books/:id: allowed for all authenticated roles

## Dependencies
- REQ-RBAC-001, REQ-BOOK-002

## Test
`TestBookRBAC` in test module
