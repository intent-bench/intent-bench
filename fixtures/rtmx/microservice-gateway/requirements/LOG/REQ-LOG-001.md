# REQ-LOG-001: Structured JSON Logging

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Log every proxied request in structured JSON format to enable machine parsing, log aggregation, and operational debugging. Each log entry must capture the full request lifecycle including timing, routing decisions, and response status. Errors must include contextual information to aid diagnosis.

## Acceptance Criteria

1. Every proxied request produces a JSON log entry written to stdout.
2. Each log entry includes the fields: timestamp (ISO 8601), request_id (UUID), method, path, target_service, status_code, and latency_ms.
3. Each log entry includes the client IP address in a `client_ip` field.
4. Each log entry includes the api_key_id (not the key value) of the authenticated caller.
5. Error responses (status >= 500) are logged at the "error" level.
6. Client error responses (status 400-499) are logged at the "warn" level.
7. Successful responses (status 200-299) are logged at the "info" level.
8. Log entries for errors include an `error` field with a descriptive message.
9. The log output is valid JSON with one entry per line (JSONL format).
10. Gateway startup and shutdown events are logged with a "lifecycle" event type.
11. Requests to /health are not logged at the info level to avoid log noise (debug level only).

## API Endpoints

Not applicable. This is an internal logging requirement.

### Example Log Entry

```json
{
  "timestamp": "2026-01-01T00:00:00Z",
  "level": "info",
  "event": "proxy_request",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/users/123",
  "target_service": "users-service",
  "client_ip": "192.168.1.1",
  "api_key_id": 5,
  "status_code": 200,
  "latency_ms": 42
}
```

## Dependencies

- REQ-AUTH-002: Authentication middleware must be in place to provide the api_key_id for log entries.
