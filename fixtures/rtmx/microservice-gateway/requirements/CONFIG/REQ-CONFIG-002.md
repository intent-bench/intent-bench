# REQ-CONFIG-002: Configuration Hot-Reload

## Status: MISSING
## Priority: HIGH
## Phase: 9

## Requirement

Support hot-reloading of the gateway YAML configuration file via an admin API endpoint, allowing operators to update services, routes, rate limits, and circuit breaker settings without restarting the gateway. The reload operation must validate the new configuration before applying it and provide a rollback path if validation fails.

## Acceptance Criteria

1. POST /admin/config/reload triggers a re-read and re-parse of the YAML configuration file.
2. The reload endpoint requires an admin API key (returns 401 without one, 403 with a service-role key).
3. The new configuration is validated before applying: valid YAML syntax, required fields present, service references in routes resolve to defined services.
4. If validation fails, the reload returns HTTP 400 with a descriptive error message and the running configuration remains unchanged.
5. On successful reload, new services defined in the YAML are registered in the database.
6. On successful reload, routes are updated to match the new YAML definitions.
7. On successful reload, rate_limit.default_rpm and circuit_breaker settings are updated in the running configuration.
8. The reload response includes a summary of changes: services_added, services_removed, routes_added, routes_removed.
9. Existing in-flight requests are not affected by the reload; new configuration applies only to subsequent requests.
10. The gateway logs a lifecycle event at "info" level when configuration is successfully reloaded.
11. Rate limit counters and circuit breaker states are preserved across reloads; only configuration thresholds change.

## API Endpoints

### Reload Configuration

**POST /admin/config/reload**

Request Headers:
```
X-API-Key: admin-key-value
```

Response (200 OK):
```json
{
  "status": "reloaded",
  "changes": {
    "services_added": 1,
    "services_removed": 0,
    "routes_added": 2,
    "routes_removed": 1
  },
  "timestamp": "2026-01-01T12:00:00Z"
}
```

### Reload with Validation Error

**POST /admin/config/reload**

Response (400 Bad Request):
```json
{
  "error": "validation_failed",
  "message": "Route '/api/payments/*' references undefined service 'payments-service'",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

## Dependencies

- REQ-CONFIG-001: YAML configuration file parsing must be implemented as the foundation for reload.
- REQ-METRICS-002: Metrics endpoint must be in place to ensure reload does not disrupt metrics collection.
