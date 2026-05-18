# REQ-AUTH-002: User Login

## Requirement
POST /auth/login returns JWT token for valid credentials.

## Acceptance Criteria
- Accepts username and password
- Returns 200 with `token` field containing a valid JWT
- JWT payload includes user id and role
- Invalid credentials return 401
- Token is signed with a server secret

## Dependencies
- REQ-AUTH-001 (users must exist to login)

## Test
`TestLogin` in test module
