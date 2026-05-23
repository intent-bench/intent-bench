# REQ-CIRCUIT-002: Circuit Breaker Admin Endpoints

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement admin endpoints for viewing and managing circuit breaker state. Operators must be able to inspect the current state of all circuit breakers and manually reset a circuit breaker to the closed state for operational recovery.

## Acceptance Criteria

1. GET /admin/circuit-breakers returns 200 with the current state of all circuit breakers.
2. Each circuit breaker entry includes service_id, service_name, state, failure_count, last_failure timestamp, and opened_at timestamp.
3. GET /admin/circuit-breakers returns an empty array when no services are registered.
4. POST /admin/circuit-breakers/:service_id/reset transitions the circuit breaker to closed and resets failure_count to 0.
5. POST /admin/circuit-breakers/:service_id/reset returns 200 with the updated circuit breaker state.
6. POST /admin/circuit-breakers/:service_id/reset returns 404 when the service_id does not exist.
7. Resetting a circuit breaker that is already closed returns 200 with no state change.
8. Both endpoints require admin role authentication.

## API Endpoints

### GET /admin/circuit-breakers

Response (200):
```json
[
  {
    "service_id": 1,
    "service_name": "users-service",
    "state": "open",
    "failure_count": 5,
    "last_failure": "2026-01-15T10:55:30Z",
    "opened_at": "2026-01-15T10:55:30Z"
  },
  {
    "service_id": 2,
    "service_name": "orders-service",
    "state": "closed",
    "failure_count": 0,
    "last_failure": null,
    "opened_at": null
  }
]
```

### POST /admin/circuit-breakers/:service_id/reset

Response (200):
```json
{
  "service_id": 1,
  "service_name": "users-service",
  "state": "closed",
  "failure_count": 0,
  "last_failure": null,
  "opened_at": null,
  "message": "circuit breaker reset to closed"
}
```

## Dependencies

- REQ-CIRCUIT-001: Circuit breaker state machine must exist before admin endpoints can inspect or modify it.
