# REQ-HEALTH-002: Background Health Checker

## Status: MISSING
## Priority: P0
## Phase: 8

## Requirement

Run a background process that periodically polls each registered backend service's health check path and updates the service's is_healthy status and last_health_check timestamp in the database. The health checker detects service degradation proactively, enabling the circuit breaker to open before user-facing requests accumulate failures.

## Acceptance Criteria

1. The background health checker polls each registered service's health_check_path every 30 seconds by default.
2. The polling interval is configurable via gateway YAML configuration.
3. A service is marked is_healthy=true when its health check endpoint returns HTTP 200.
4. A service is marked is_healthy=false when its health check endpoint returns a non-200 status code or the request times out.
5. The last_health_check timestamp is updated after every poll attempt regardless of the result.
6. When a previously healthy service becomes unhealthy, the circuit breaker for that service transitions to the open state.
7. The health checker uses a configurable timeout per health check request (default 5 seconds).
8. The health checker runs in a separate goroutine/thread and does not block request processing.
9. When a new service is registered via the admin API, the health checker begins polling it within one polling interval.
10. When a service is deregistered via the admin API, the health checker stops polling it.
11. Health check requests are not recorded in the audit log and do not count against rate limits.

## API Endpoints

Not applicable. This is a background process. Health check results are visible through:

**GET /health/services** (see REQ-HEALTH-001)

Response (200 OK):
```json
[
  {
    "name": "users-service",
    "is_healthy": true,
    "last_health_check": "2026-01-01T00:01:00Z"
  }
]
```

**GET /admin/services**

Response (200 OK):
```json
[
  {
    "id": 1,
    "name": "users-service",
    "base_url": "http://localhost:3001",
    "health_check_path": "/health",
    "is_healthy": true,
    "last_health_check": "2026-01-01T00:01:00Z",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

## Dependencies

- REQ-RETRY-002: Retry safety must be in place so health check polling does not interact with retry logic.
- REQ-HEALTH-001: Gateway health endpoint must exist as the foundation for health reporting.
