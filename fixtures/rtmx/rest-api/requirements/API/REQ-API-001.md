# REQ-API-001: Health Check

## Requirement
GET /health returns 200 without authentication.

## Acceptance Criteria
- Returns 200 with `{"status": "ok"}`
- No authentication required

## Test
`TestHealthCheck` in test module
