# REQ-AUTH-003: User Profile

## Requirement
GET /auth/me returns authenticated user's profile.

## Acceptance Criteria
- Requires valid JWT in Authorization header (Bearer scheme)
- Returns 200 with user object (id, username, email, role)
- Returns 401 if token is missing or invalid

## Dependencies
- REQ-AUTH-001, REQ-AUTH-002

## Test
`TestProfile` in test module
