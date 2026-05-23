# REQ-REG-001: Service Registry CRUD

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Implement admin CRUD endpoints for registering and managing backend services in the gateway. Services must be registered before routes can target them. Each service has a name, base URL, and health check path that the gateway uses to proxy requests and monitor backend health.

## Acceptance Criteria

1. POST /admin/services creates a new service with name, base_url, and optional health_check_path.
2. POST /admin/services returns 201 with the created service including its assigned id.
3. GET /admin/services returns 200 with an array of all registered services including health status.
4. GET /admin/services/:id returns 200 with the service details for a valid id.
5. GET /admin/services/:id returns 404 when the service id does not exist.
6. PUT /admin/services/:id updates the service name, base_url, or health_check_path and returns 200.
7. PUT /admin/services/:id returns 404 when the service id does not exist.
8. DELETE /admin/services/:id removes the service and returns 204.
9. DELETE /admin/services/:id returns 404 when the service id does not exist.
10. Creating a service with a duplicate name returns 409 Conflict.
11. Creating a service without a required field (name, base_url) returns 422 with a descriptive error.

## API Endpoints

### POST /admin/services

Request:
```json
{
  "name": "users-service",
  "base_url": "http://localhost:3001",
  "health_check_path": "/health"
}
```

Response (201):
```json
{
  "id": 1,
  "name": "users-service",
  "base_url": "http://localhost:3001",
  "health_check_path": "/health",
  "is_healthy": true,
  "last_health_check": null,
  "created_at": "2026-01-15T10:30:00Z"
}
```

### GET /admin/services

Response (200):
```json
[
  {
    "id": 1,
    "name": "users-service",
    "base_url": "http://localhost:3001",
    "health_check_path": "/health",
    "is_healthy": true,
    "last_health_check": "2026-01-15T10:31:00Z",
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

### DELETE /admin/services/:id

Response (204): No content.

## Dependencies

- REQ-DB-001: Database schema must exist before services can be persisted.
