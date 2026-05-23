# REQ-ROUTE-001: Route Management CRUD

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement admin CRUD endpoints for managing route definitions that map URL path patterns to registered backend services. Routes define the core proxy behavior of the gateway, including which service handles a given path, the HTTP method filter, timeout, prefix stripping, and per-route middleware configuration.

## Acceptance Criteria

1. POST /admin/routes creates a new route with path_pattern, method, service_id, strip_prefix, timeout_ms, and middleware_config.
2. POST /admin/routes returns 201 with the created route including its assigned id.
3. POST /admin/routes returns 422 when service_id references a non-existent service.
4. GET /admin/routes returns 200 with an array of all routes including their associated service name.
5. PUT /admin/routes/:id updates route fields and returns 200 with the updated route.
6. PUT /admin/routes/:id returns 404 when the route id does not exist.
7. DELETE /admin/routes/:id removes the route and returns 204.
8. DELETE /admin/routes/:id returns 404 when the route id does not exist.
9. Creating a route with a missing path_pattern returns 422 with a descriptive error.
10. The middleware_config field accepts a JSON object with keys for rate_limit, cache_ttl_seconds, max_retries, and cors.

## API Endpoints

### POST /admin/routes

Request:
```json
{
  "path_pattern": "/api/users/*",
  "method": "*",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "rate_limit": 50,
    "cache_ttl_seconds": 60,
    "max_retries": 2,
    "cors": {
      "allowed_origins": ["*"]
    }
  }
}
```

Response (201):
```json
{
  "id": 1,
  "path_pattern": "/api/users/*",
  "method": "*",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "rate_limit": 50,
    "cache_ttl_seconds": 60,
    "max_retries": 2,
    "cors": {
      "allowed_origins": ["*"]
    }
  },
  "created_at": "2026-01-15T10:35:00Z"
}
```

### GET /admin/routes

Response (200):
```json
[
  {
    "id": 1,
    "path_pattern": "/api/users/*",
    "method": "*",
    "service_id": 1,
    "service_name": "users-service",
    "strip_prefix": true,
    "timeout_ms": 5000,
    "middleware_config": {
      "rate_limit": 50,
      "cache_ttl_seconds": 60
    },
    "created_at": "2026-01-15T10:35:00Z"
  }
]
```

## Dependencies

- REQ-REG-001: Services must be registered before routes can reference them.
