# REQ-METRICS-002: Metrics Admin Endpoint

## Status: MISSING
## Priority: HIGH
## Phase: 8

## Requirement

Expose an admin endpoint at GET /admin/metrics that returns aggregated metrics from in-memory counters and the audit log. The endpoint provides per-service statistics (total requests, success/error counts, average latency), per-route statistics (request count, cache hit rate), and global gateway statistics. Access requires an admin API key.

## Acceptance Criteria

1. GET /admin/metrics returns HTTP 200 with a JSON response containing per_service, per_route, and global sections.
2. Per-service metrics include: total_requests, success_count, error_count, avg_latency_ms, and p99_latency_ms.
3. Per-route metrics include: request_count, cache_hit_rate (as a decimal between 0.0 and 1.0).
4. Global metrics include: total_requests, active_connections, and uptime_seconds.
5. The avg_latency_ms is rounded to two decimal places.
6. The p99_latency_ms is computed from the audit log entries for each service.
7. The endpoint requires an admin API key (returns 401 without one, 403 with a service-role key).
8. The response includes a `computed_at` timestamp in ISO 8601 UTC format.
9. When no requests have been processed, all counters return 0 and cache_hit_rate returns 0.0.
10. The endpoint responds within 500ms even when the audit log contains thousands of entries.

## API Endpoints

### Get Metrics

**GET /admin/metrics**

Request Headers:
```
X-API-Key: admin-key-value
```

Response (200 OK):
```json
{
  "computed_at": "2026-01-01T12:00:00Z",
  "per_service": {
    "users-service": {
      "total_requests": 1500,
      "success_count": 1450,
      "error_count": 50,
      "avg_latency_ms": 42.00,
      "p99_latency_ms": 195
    },
    "orders-service": {
      "total_requests": 800,
      "success_count": 790,
      "error_count": 10,
      "avg_latency_ms": 85.50,
      "p99_latency_ms": 320
    }
  },
  "per_route": {
    "/api/users/*": {
      "request_count": 1200,
      "cache_hit_rate": 0.67
    },
    "/api/orders/*": {
      "request_count": 800,
      "cache_hit_rate": 0.0
    }
  },
  "global": {
    "total_requests": 2300,
    "active_connections": 5,
    "uptime_seconds": 7200
  }
}
```

## Dependencies

- REQ-METRICS-001: In-memory counters must be implemented to provide the data for this endpoint.
- REQ-HEALTH-002: Backend health checker must be in place as health status informs operational metrics context.
