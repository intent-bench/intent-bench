# REQ-AUDIT-001: Audit Log for Proxied Requests

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Record an audit log entry in the database for every proxied request, capturing the API key used, HTTP method, request path, target backend service, response status code, and request latency. The audit log supports compliance requirements, usage analytics, and serves as the data source for metrics aggregation.

## Acceptance Criteria

1. Every proxied request that reaches the backend (or is rejected by the circuit breaker) creates an audit log entry in the audit_log database table.
2. Each audit log entry includes: id, timestamp, api_key_id, method, path, target_service, status_code, and latency_ms.
3. The timestamp is recorded in ISO 8601 UTC format.
4. The latency_ms captures the total time from request receipt to response completion in milliseconds.
5. Requests rejected by rate limiting (429) are recorded in the audit log with status_code 429.
6. Requests rejected by the circuit breaker (503) are recorded in the audit log with status_code 503.
7. The GET /admin/audit-log endpoint returns paginated audit log entries sorted by timestamp descending.
8. The audit log endpoint supports query filters: service, method, from (timestamp), and to (timestamp).
9. The audit log endpoint requires an admin API key.
10. Audit log entries are never deleted through normal operation; they are append-only.
11. Health check requests (GET /health) are excluded from the audit log.

## API Endpoints

### Query Audit Log

**GET /admin/audit-log?service=users-service&method=GET&from=2026-01-01T00:00:00Z&to=2026-01-02T00:00:00Z**

Request Headers:
```
X-API-Key: admin-key-value
```

Response (200 OK):
```json
{
  "entries": [
    {
      "id": 42,
      "timestamp": "2026-01-01T12:30:00Z",
      "api_key_id": 5,
      "method": "GET",
      "path": "/api/users/123",
      "target_service": "users-service",
      "status_code": 200,
      "latency_ms": 45
    },
    {
      "id": 41,
      "timestamp": "2026-01-01T12:29:55Z",
      "api_key_id": 5,
      "method": "GET",
      "path": "/api/users",
      "target_service": "users-service",
      "status_code": 200,
      "latency_ms": 38
    }
  ],
  "total": 2
}
```

## Dependencies

- REQ-AUTH-002: Authentication middleware must be in place to provide the api_key_id for each audit entry.
