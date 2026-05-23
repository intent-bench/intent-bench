# REQ-VALID-001: Input Validation on Admin Endpoints

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Validate all input data on admin API endpoints and return HTTP 422 Unprocessable Entity with descriptive error messages when validation fails. Validation must cover required fields, data types, value constraints, and referential integrity to prevent invalid configuration from being persisted to the database.

## Acceptance Criteria

1. POST /admin/services returns 422 when the `name` field is missing or empty.
2. POST /admin/services returns 422 when the `base_url` field is not a valid URL.
3. POST /admin/services returns 422 when the `name` is already taken by an existing service.
4. POST /admin/routes returns 422 when the `path_pattern` field is missing or empty.
5. POST /admin/routes returns 422 when the `service_id` references a non-existent service.
6. POST /admin/routes returns 422 when the `method` is not a valid HTTP method or "*".
7. POST /admin/routes returns 422 when `timeout_ms` is negative or zero.
8. POST /admin/keys returns 422 when the `name` field is missing or empty.
9. POST /admin/keys returns 422 when the `role` is not "admin" or "service".
10. All 422 responses include a JSON body with `error` and `message` fields describing the validation failure.
11. Multiple validation errors on a single request are returned together in a `details` array.
12. Valid requests that pass all validation checks are processed normally and return the expected success response.

## API Endpoints

### Validation Error Response

**POST /admin/services**

Request:
```json
{
  "name": "",
  "base_url": "not-a-url"
}
```

Response (422 Unprocessable Entity):
```json
{
  "error": "validation_failed",
  "message": "Input validation failed",
  "details": [
    {"field": "name", "message": "name is required and must not be empty"},
    {"field": "base_url", "message": "base_url must be a valid HTTP or HTTPS URL"}
  ]
}
```

### Route Validation Error

**POST /admin/routes**

Request:
```json
{
  "path_pattern": "/api/users/*",
  "service_id": 999,
  "method": "INVALID",
  "timeout_ms": -1
}
```

Response (422 Unprocessable Entity):
```json
{
  "error": "validation_failed",
  "message": "Input validation failed",
  "details": [
    {"field": "service_id", "message": "service with id 999 does not exist"},
    {"field": "method", "message": "method must be a valid HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) or '*'"},
    {"field": "timeout_ms", "message": "timeout_ms must be a positive integer"}
  ]
}
```

## Dependencies

- REQ-DB-001: Database schema must exist so that referential integrity checks (e.g., service_id exists) can be performed.
