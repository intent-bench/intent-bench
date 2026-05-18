# REQ-AUTH-001: User Registration

## Requirement
POST /auth/register creates user with hashed password and default viewer role.

## Acceptance Criteria
- Accepts username, email, password in request body
- Password is hashed before storage (bcrypt or argon2)
- Default role is "viewer"
- Returns 201 with user object (id, username, email, role, created_at)
- Password hash is never returned in any response
- Duplicate username or email returns 409

## Test
`TestRegister` in test module
