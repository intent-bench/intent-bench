# REQ-HEALTH-001: Gateway Health Endpoint

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Provide a health check endpoint at GET /health that returns HTTP 200 whenever the gateway process is running and able to accept requests. This endpoint serves as the target for external load balancers and orchestration platforms to determine gateway availability. The endpoint must not require authentication and must respond with minimal latency.

## Acceptance Criteria

1. GET /health returns HTTP 200 OK when the gateway is running.
2. The response body is a JSON object containing at minimum: `{"status": "healthy"}`.
3. The response includes a `timestamp` field with the current ISO 8601 UTC time.
4. The response includes an `uptime_seconds` field indicating how long the gateway has been running.
5. The /health endpoint does not require an X-API-Key header.
6. The /health endpoint does not count against rate limits for any API key.
7. The /health endpoint is not recorded in the audit log.
8. The response Content-Type is application/json.
9. GET /health/services returns a JSON array with the health status of all registered backend services, including service name, is_healthy flag, and last_health_check timestamp.
10. GET /health/services returns an empty array when no services are registered.

## API Endpoints

### Gateway Health

**GET /health**

Response (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "uptime_seconds": 3600
}
```

### Service Health Summary

**GET /health/services**

Response (200 OK):
```json
[
  {
    "name": "users-service",
    "is_healthy": true,
    "last_health_check": "2026-01-01T00:00:30Z"
  },
  {
    "name": "orders-service",
    "is_healthy": false,
    "last_health_check": "2026-01-01T00:00:30Z"
  }
]
```

## Dependencies

- REQ-REG-001: Service registry must exist so that /health/services can report on registered backend services.
