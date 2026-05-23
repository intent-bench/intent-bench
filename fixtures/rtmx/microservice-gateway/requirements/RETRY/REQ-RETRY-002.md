# REQ-RETRY-002: Retry Safety for Non-Idempotent Methods

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Ensure that retry logic does not automatically retry non-idempotent HTTP methods (POST, PATCH, DELETE) to prevent duplicate side effects on backend services. Non-idempotent methods must only be retried when explicitly enabled in the route middleware configuration via a retry_non_idempotent flag.

## Acceptance Criteria

1. GET, HEAD, OPTIONS, and PUT requests are retried automatically according to the route retry policy.
2. POST requests are NOT retried by default when the backend returns 502, 503, or 504.
3. PATCH requests are NOT retried by default when the backend returns 502, 503, or 504.
4. DELETE requests are NOT retried by default when the backend returns 502, 503, or 504.
5. When a route middleware_config includes `retry_non_idempotent: true`, POST/PATCH/DELETE requests are retried according to the normal retry policy.
6. When retry_non_idempotent is false or absent, non-idempotent methods return the original error response immediately without retrying.
7. The retry safety check occurs before the exponential backoff calculation to avoid unnecessary delay.
8. Circuit breaker failure counts still increment on the initial failed request even when retries are suppressed.
9. Audit log entries for non-retried failures record retry_count as 0.
10. The gateway logs a debug-level message when a retry is suppressed due to method safety.

## API Endpoints

### Route Configuration with Retry Safety Override

**PUT /admin/routes/:id**

Request:
```json
{
  "path_pattern": "/api/orders/*",
  "method": "POST",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "max_retries": 2,
    "retry_non_idempotent": true
  }
}
```

Response (200 OK):
```json
{
  "id": 3,
  "path_pattern": "/api/orders/*",
  "method": "POST",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "max_retries": 2,
    "retry_non_idempotent": true
  },
  "created_at": "2026-01-01T00:00:00Z"
}
```

## Dependencies

- REQ-RETRY-001: Retry with exponential backoff must be implemented before safety restrictions can be applied.
