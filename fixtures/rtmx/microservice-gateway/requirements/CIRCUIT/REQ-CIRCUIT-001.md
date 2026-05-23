# REQ-CIRCUIT-001: Circuit Breaker State Machine

## Status: MISSING
## Priority: P0
## Phase: 6

## Requirement

Implement a per-service circuit breaker using the closed/open/half_open state machine pattern. The circuit breaker monitors backend failures and short-circuits requests when a service is unhealthy, preventing cascading failures. Thresholds for failure count and recovery timeout are configurable.

## Acceptance Criteria

1. Each registered service has its own independent circuit breaker starting in the closed state.
2. In the closed state, all requests are forwarded to the backend normally.
3. After 5 consecutive failures (configurable via failure_threshold), the circuit transitions from closed to open.
4. In the open state, all requests are immediately rejected with 503 Service Unavailable without contacting the backend.
5. After 30 seconds (configurable via recovery_timeout_seconds), the circuit transitions from open to half_open.
6. In the half_open state, the next request is forwarded to the backend as a probe.
7. If the probe request succeeds, the circuit transitions from half_open to closed and resets the failure count.
8. If the probe request fails, the circuit transitions from half_open back to open and the recovery timer restarts.
9. A 502, 503, or 504 response from the backend counts as a failure.
10. A successful response (2xx) resets the consecutive failure count to 0 in the closed state.
11. Circuit breaker state is stored in memory and does not persist across gateway restarts.
12. The 503 response body includes the service name and circuit breaker state.

## API Endpoints

### Circuit breaker open response

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (503):
```json
{
  "error": "service unavailable",
  "service": "users-service",
  "circuit_state": "open",
  "retry_after_seconds": 30
}
```

## Dependencies

- REQ-CACHE-002: Cache control must be in place so cached responses can be served even when the circuit is open.
