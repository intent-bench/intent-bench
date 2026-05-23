# REQ-METRICS-001: Per-Service and Per-Route Request Metrics

## Status: MISSING
## Priority: HIGH
## Phase: 8

## Requirement

Track request metrics per service and per route using in-memory counters updated on every proxied request. Metrics include total request count, success count, error count, and average latency per service. Per-route metrics include request count and cache hit rate. These counters provide the data source for the metrics admin endpoint.

## Acceptance Criteria

1. Per-service counters track: total_requests, success_count (2xx), error_count (4xx and 5xx), and total_latency_ms.
2. Average latency per service is computed as total_latency_ms / total_requests.
3. Per-route counters track: request_count, cache_hits, and cache_misses.
4. Cache hit rate per route is computed as cache_hits / (cache_hits + cache_misses).
5. Global counters track: total_requests across all services and active_connections (concurrent in-flight requests).
6. Counters are updated atomically to prevent race conditions under concurrent requests.
7. Counter values persist across requests but reset on gateway restart (in-memory only).
8. Requests rejected by the circuit breaker (503) increment the service error_count.
9. Requests rejected by rate limiting (429) are counted in global total_requests but not in per-service counters.
10. The metrics counters are also reconcilable against the audit log for consistency verification.

## API Endpoints

Not applicable. Metrics are exposed through REQ-METRICS-002 (metrics admin endpoint). This requirement defines the internal counters and tracking logic.

### Internal Counter Structure

```json
{
  "per_service": {
    "users-service": {
      "total_requests": 1500,
      "success_count": 1450,
      "error_count": 50,
      "total_latency_ms": 63000
    }
  },
  "per_route": {
    "/api/users/*": {
      "request_count": 1200,
      "cache_hits": 800,
      "cache_misses": 400
    }
  },
  "global": {
    "total_requests": 5000,
    "active_connections": 12
  }
}
```

## Dependencies

- REQ-AUDIT-001: Audit log provides the persistent data source that metrics can be reconciled against.
