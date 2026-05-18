# REQ-AUTH-005: Authentication Rejection

## Requirement
Missing or invalid tokens return 401 on all protected endpoints.

## Acceptance Criteria
- No Authorization header: 401
- Malformed token: 401
- Expired token: 401
- Applies to all endpoints except /health and /auth/register and /auth/login

## Dependencies
- REQ-AUTH-002

## Test
`TestUnauthorized` in test module
