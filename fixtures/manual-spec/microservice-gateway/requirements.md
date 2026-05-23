# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-CONFIG-001: YAML configuration file parsing

**Phase:** 1

*Configuration drives all gateway behavior*

### Acceptance Criteria

1. The gateway reads a YAML configuration file from a path specified by a command-line argument or environment variable (default: gateway.yaml).
2. The gateway.port field sets the HTTP listening port (default: 8080).
3. The gateway.log_level field sets the initial log level (default: info).
4. The services array pre-registers backend services with name, base_url, and health_check_path.
5. The routes array defines route mappings with path, service, method, strip_prefix, timeout_ms, and middleware configuration.
6. The rate_limit.default_rpm field sets the default requests-per-minute limit (default: 100).
7. The circuit_breaker.failure_threshold field sets the consecutive failure count before opening (default: 5).
8. The circuit_breaker.recovery_timeout_seconds field sets the open-to-half-open transition delay (default: 30).
9. If the configuration file does not exist or is malformed, the gateway exits with a non-zero exit code and a descriptive error message.
10. Services and routes defined in the YAML file are persisted to the SQLite database on startup.
11. The gateway logs the loaded configuration summary at startup (number of services, routes, and settings).

### API

### Configuration File Format

```yaml
gateway:
  port: 8080
  log_level: info

services:
  - name: users-service
    base_url: http://localhost:3001
    health_check_path: /health
  - name: orders-service
    base_url: http://localhost:3002
    health_check_path: /health

routes:
  - path: /api/users/*
    service: users-service
    method: "*"
    strip_prefix: true
    timeout_ms: 5000
    middleware:
      rate_limit: 50
      cache_ttl_seconds: 60
      max_retries: 2
      cors:
        allowed_origins: ["*"]

rate_limit:
  default_rpm: 100

circuit_breaker:
  failure_threshold: 5
  recovery_timeout_seconds: 30
```

### GET /admin/config

**Request Headers:**
```
X-API-Key: admin-key-value
```

**Response (200 OK):**
```json
{
  "gateway": {
    "port": 8080,
    "log_level": "info"
  },
  "services_count": 2,
  "routes_count": 1,
  "rate_limit": {
    "default_rpm": 100
  },
  "circuit_breaker": {
    "failure_threshold": 5,
    "recovery_timeout_seconds": 30
  }
}
```

---

## 2. REQ-DB-001: Database setup with SQLite for persistent gateway state

**Phase:** 1

*Foundation: services, routes, keys, and audit log tables*

### Acceptance Criteria

1. A SQLite database file is created on application startup if it does not already exist.
2. The `services` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT UNIQUE NOT NULL), base_url (TEXT NOT NULL), health_check_path (TEXT NOT NULL DEFAULT '/health'), is_healthy (INTEGER NOT NULL DEFAULT 1), last_health_check (TEXT), created_at (TEXT NOT NULL).
3. The `routes` table exists with columns: id (INTEGER PRIMARY KEY), path_pattern (TEXT NOT NULL), method (TEXT NOT NULL DEFAULT '*'), service_id (INTEGER NOT NULL REFERENCES services(id)), strip_prefix (INTEGER NOT NULL DEFAULT 0), timeout_ms (INTEGER NOT NULL DEFAULT 5000), middleware_config (TEXT DEFAULT '{}'), created_at (TEXT NOT NULL).
4. The `api_keys` table exists with columns: id (INTEGER PRIMARY KEY), key_hash (TEXT UNIQUE NOT NULL), name (TEXT NOT NULL), role (TEXT NOT NULL CHECK(role IN ('admin', 'service'))), rate_limit_override (INTEGER), is_active (INTEGER NOT NULL DEFAULT 1), created_at (TEXT NOT NULL).
5. The `audit_log` table exists with columns: id (INTEGER PRIMARY KEY), timestamp (TEXT NOT NULL), api_key_id (INTEGER REFERENCES api_keys(id)), method (TEXT NOT NULL), path (TEXT NOT NULL), target_service (TEXT NOT NULL), status_code (INTEGER NOT NULL), latency_ms (REAL NOT NULL).
6. Foreign key enforcement is enabled (PRAGMA foreign_keys = ON).
7. Indexes exist on: routes(service_id), routes(path_pattern), api_keys(key_hash), audit_log(timestamp), audit_log(target_service).
8. A schema_version table tracks the current schema version number.
9. Inserting a route with a non-existent service_id is rejected by the foreign key constraint.
10. The middleware_config column in routes stores valid JSON as TEXT.

### API

Not applicable. This is an internal infrastructure requirement.

---

## 3. REQ-VALID-001: Input validation on all admin endpoints

**Phase:** 2

**Depends on:** REQ-DB-001

*Prevents invalid configuration*

### Acceptance Criteria

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

### API

### POST /admin/services (validation error)

**Request:**
```json
{
  "name": "",
  "base_url": "not-a-url"
}
```

**Response (422 Unprocessable Entity):**
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

### POST /admin/routes (validation error)

**Request:**
```json
{
  "path_pattern": "/api/users/*",
  "service_id": 999,
  "method": "INVALID",
  "timeout_ms": -1
}
```

**Response (422 Unprocessable Entity):**
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

---

## 4. REQ-REG-001: Service registry for backend service management

**Phase:** 1

**Depends on:** REQ-DB-001

*Services must be registered before routes can target them*

### Acceptance Criteria

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

### API

### POST /admin/services

**Request:**
```json
{
  "name": "users-service",
  "base_url": "http://localhost:3001",
  "health_check_path": "/health"
}
```

**Response (201 Created):**
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

**Response (200 OK):**
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

**Response (204 No Content)**

---

## 5. REQ-HEALTH-001: Gateway health endpoint

**Phase:** 2

**Depends on:** REQ-REG-001

*Load balancer health check target*

### Acceptance Criteria

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

### API

### GET /health

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "uptime_seconds": 3600
}
```

### GET /health/services

**Response (200 OK):**
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

---

## 6. REQ-ROUTE-001: Route management with path pattern matching

**Phase:** 2

**Depends on:** REQ-REG-001

*Routes define the gateway proxy behavior*

### Acceptance Criteria

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

### API

### POST /admin/routes

**Request:**
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

**Response (201 Created):**
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

**Response (200 OK):**
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

---

## 7. REQ-ROUTE-002: Path pattern matching and method filtering

**Phase:** 2

**Depends on:** REQ-ROUTE-001

*Request routing logic for the proxy*

### Acceptance Criteria

1. A route with path_pattern `/api/users/*` matches requests to `/api/users/123` and `/api/users/123/profile`.
2. A route with path_pattern `/api/users` (no wildcard) matches only the exact path `/api/users`.
3. When multiple routes match, the most specific pattern wins (e.g., `/api/users/admin` beats `/api/users/*`).
4. A route with method `*` matches all HTTP methods (GET, POST, PUT, DELETE, PATCH).
5. A route with method `GET` matches only GET requests; POST to the same path returns 404 if no other route matches.
6. A request to a path with no matching route returns 404 with a JSON error body.
7. Route matching is case-sensitive for path segments.
8. The matched route is passed to the middleware chain for processing.
9. A route with path_pattern `/api/v1/*` does not match `/api/v2/users`.
10. Trailing slashes are normalized so `/api/users/` and `/api/users` match the same route.

### API

### Proxy request (matched route)

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response: Proxied from the backend service associated with the matching route.

### Proxy request (no matching route)

**Request:**
```
GET /unknown/path HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (404 Not Found):**
```json
{
  "error": "no route matches path /unknown/path"
}
```

---

## 8. REQ-AUTH-001: API key management with role-based access

**Phase:** 2

**Depends on:** REQ-ROUTE-001

*Authentication is the first middleware in the chain*

### Acceptance Criteria

1. POST /admin/keys creates a new API key with name and role (admin or service).
2. POST /admin/keys returns 201 with the generated key value, id, name, and role.
3. The raw API key is returned only in the POST response and never again.
4. The key is stored as a cryptographic hash (SHA-256 or bcrypt) in the api_keys table.
5. GET /admin/keys returns 200 with an array of all keys showing id, name, role, is_active, and created_at but not the key value or hash.
6. DELETE /admin/keys/:id sets is_active to 0 (soft delete) and returns 204.
7. DELETE /admin/keys/:id returns 404 when the key id does not exist.
8. Creating a key with an invalid role (not admin or service) returns 422.
9. An optional rate_limit_override field sets a per-key rate limit that overrides the global default.
10. Creating a key without a required field (name, role) returns 422 with a descriptive error.

### API

### POST /admin/keys

**Request:**
```json
{
  "name": "ci-pipeline",
  "role": "service",
  "rate_limit_override": 200
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "key": "sk_live_a1b2c3d4e5f6g7h8i9j0",
  "name": "ci-pipeline",
  "role": "service",
  "rate_limit_override": 200,
  "is_active": true,
  "created_at": "2026-01-15T10:40:00Z"
}
```

### GET /admin/keys

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "ci-pipeline",
    "role": "service",
    "rate_limit_override": 200,
    "is_active": true,
    "created_at": "2026-01-15T10:40:00Z"
  }
]
```

### DELETE /admin/keys/:id

**Response (204 No Content)**

---

## 9. REQ-CORS-001: CORS preflight handling

**Phase:** 4

**Depends on:** REQ-ROUTE-001

*Cross-origin browser access support*

### Acceptance Criteria

1. An OPTIONS request to a route with CORS middleware configured returns a 204 No Content response without proxying to the backend.
2. The preflight response includes the Access-Control-Allow-Origin header matching the request Origin if it is in the allowed_origins list.
3. The preflight response includes Access-Control-Allow-Methods listing the methods from the route CORS allowed_methods configuration.
4. The preflight response includes Access-Control-Allow-Headers listing the headers from the route CORS allowed_headers configuration.
5. The preflight response includes Access-Control-Max-Age set to the route CORS max_age value in seconds.
6. When allowed_origins is ["*"], the Access-Control-Allow-Origin header is set to "*".
7. When the request Origin is not in the allowed_origins list, the preflight response omits the Access-Control-Allow-Origin header and returns 204 with no CORS headers.
8. An OPTIONS request to a route without CORS middleware configured returns 404 or passes through the normal routing logic.
9. Preflight responses are not recorded in the audit log as proxied requests.
10. The gateway does not require API key authentication for OPTIONS preflight requests on CORS-enabled routes.

### API

### Route with CORS middleware configuration

**POST /admin/routes**

**Request:**
```json
{
  "path_pattern": "/api/users/*",
  "method": "*",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "cors": {
      "allowed_origins": ["https://example.com", "https://app.example.com"],
      "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
      "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"],
      "max_age": 3600
    }
  }
}
```

### OPTIONS /api/users/123

**Request Headers:**
```
Origin: https://example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type, X-API-Key
```

**Response (204 No Content):**
```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key
Access-Control-Max-Age: 3600
```

---

## 10. REQ-AUTH-002: API key authentication middleware

**Phase:** 2

**Depends on:** REQ-AUTH-001

*All proxy requests and admin API require authentication*

### Acceptance Criteria

1. All proxy requests require an X-API-Key header; missing header returns 401 with a JSON error body.
2. An invalid API key (no matching hash in the database) returns 401.
3. A revoked API key (is_active = 0) returns 403 with a JSON error body indicating the key has been revoked.
4. A service-role key attempting to access /admin/* endpoints returns 403 with an insufficient permissions error.
5. An admin-role key can access both /admin/* endpoints and proxy endpoints.
6. A service-role key can access proxy endpoints.
7. The GET /health endpoint does not require authentication.
8. The authenticated key's id and role are attached to the request context for downstream middleware.
9. Key lookup uses the same hash algorithm as key creation (SHA-256 or bcrypt).
10. The middleware runs before rate limiting and all other middleware in the chain.

### API

### Unauthenticated request

**Request:**
```
GET /api/users/123 HTTP/1.1
```

**Response (401 Unauthorized):**
```json
{
  "error": "missing or invalid API key"
}
```

### Revoked key

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_revoked_key
```

**Response (403 Forbidden):**
```json
{
  "error": "API key has been revoked"
}
```

### Insufficient role

**Request:**
```
GET /admin/services HTTP/1.1
X-API-Key: sk_service_key
```

**Response (403 Forbidden):**
```json
{
  "error": "insufficient permissions: admin role required"
}
```

---

## 11. REQ-CORS-002: CORS response headers on all requests

**Phase:** 4

**Depends on:** REQ-CORS-001

*Browser enforces CORS on non-preflight requests too*

### Acceptance Criteria

1. Non-OPTIONS requests to CORS-enabled routes include Access-Control-Allow-Origin in the response, matching the request Origin against the allowed_origins list.
2. When allowed_origins is ["*"], Access-Control-Allow-Origin is set to "*" on all responses.
3. When the request Origin is not in the allowed_origins list, no Access-Control-Allow-Origin header is added to the response.
4. The Vary: Origin header is included in responses when allowed_origins is not ["*"] to ensure correct caching behavior.
5. Access-Control-Expose-Headers is included in the response if expose_headers is configured in the route CORS middleware.
6. Access-Control-Allow-Credentials is set to "true" when allow_credentials is enabled in the route CORS middleware.
7. When allow_credentials is true, Access-Control-Allow-Origin must not be "*" but must echo the specific origin.
8. CORS headers are added after the backend response is received, during response transformation.
9. Routes without CORS middleware configured do not have any Access-Control headers added.

### API

### GET /api/users/123 (with CORS headers)

**Request Headers:**
```
Origin: https://example.com
X-API-Key: valid-service-key
```

**Response (200 OK):**
```
Access-Control-Allow-Origin: https://example.com
Vary: Origin
Content-Type: application/json

{"id": 123, "name": "Jane Doe"}
```

### Request from disallowed origin

**Request Headers:**
```
Origin: https://evil.com
X-API-Key: valid-service-key
```

**Response (200 OK):**
```
Content-Type: application/json

{"id": 123, "name": "Jane Doe"}
```

No Access-Control-Allow-Origin header is present in the response.

---

## 12. REQ-RATE-001: Rate limiting with sliding window algorithm

**Phase:** 3

**Depends on:** REQ-AUTH-002

*Protects backends from overload*

### Acceptance Criteria

1. Each API key is limited to 100 requests per minute by default.
2. A key with rate_limit_override of 200 is allowed 200 requests per minute instead of the default.
3. A route with middleware_config rate_limit of 50 applies a per-route limit of 50 requests per minute for any key.
4. When a key exceeds its rate limit, the gateway returns 429 with a JSON error body.
5. The sliding window algorithm considers the previous window's request count proportionally.
6. Rate limit state is stored in memory (not persisted to SQLite).
7. After the window resets, the key can make requests again without restart.
8. Rate limiting runs after authentication but before proxying.
9. The per-route limit applies in addition to the per-key limit; whichever is stricter takes effect.
10. Admin endpoints are also subject to rate limiting using the same per-key limits.

### API

### Rate limit exceeded

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (429 Too Many Requests):**
```json
{
  "error": "rate limit exceeded",
  "retry_after_seconds": 32
}
```

---

## 13. REQ-LOG-001: Structured JSON request logging

**Phase:** 3

**Depends on:** REQ-AUTH-002

*Operational observability and debugging*

### Acceptance Criteria

1. Every proxied request produces a JSON log entry written to stdout.
2. Each log entry includes the fields: timestamp (ISO 8601), request_id (UUID), method, path, target_service, status_code, and latency_ms.
3. Each log entry includes the client IP address in a `client_ip` field.
4. Each log entry includes the api_key_id (not the key value) of the authenticated caller.
5. Error responses (status >= 500) are logged at the "error" level.
6. Client error responses (status 400-499) are logged at the "warn" level.
7. Successful responses (status 200-299) are logged at the "info" level.
8. Log entries for errors include an `error` field with a descriptive message.
9. The log output is valid JSON with one entry per line (JSONL format).
10. Gateway startup and shutdown events are logged with a "lifecycle" event type.
11. Requests to /health are not logged at the info level to avoid log noise (debug level only).

### API

Not applicable. This is an internal logging requirement.

### Example log entry

```json
{
  "timestamp": "2026-01-01T00:00:00Z",
  "level": "info",
  "event": "proxy_request",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/users/123",
  "target_service": "users-service",
  "client_ip": "192.168.1.1",
  "api_key_id": 5,
  "status_code": 200,
  "latency_ms": 42
}
```

---

## 14. REQ-AUDIT-001: Audit log for all proxied requests

**Phase:** 3

**Depends on:** REQ-AUTH-002

*Compliance and usage analytics*

### Acceptance Criteria

1. Every proxied request that reaches the backend (or is rejected by the circuit breaker) creates an audit log entry in the audit_log database table.
2. Each audit log entry includes: id, timestamp, api_key_id, method, path, target_service, status_code, and latency_ms.
3. The timestamp is recorded in ISO 8601 UTC format.
4. The latency_ms captures the total time from request receipt to response completion in milliseconds.
5. Requests rejected by rate limiting (429) are recorded in the audit log with status_code 429.
6. Requests rejected by the circuit breaker (503) are recorded in the audit log with status_code 503.
7. The GET /admin/audit-log endpoint returns paginated audit log entries sorted by timestamp descending.
8. The audit log endpoint supports query filters: service, method, from (timestamp), and to (timestamp).
9. The audit log endpoint requires an admin API key.
10. Audit log entries are never deleted through normal operation; they are append-only.
11. Health check requests (GET /health) are excluded from the audit log.

### API

### GET /admin/audit-log

**Request:**
```
GET /admin/audit-log?service=users-service&method=GET&from=2026-01-01T00:00:00Z&to=2026-01-02T00:00:00Z
X-API-Key: admin-key-value
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 42,
      "timestamp": "2026-01-01T12:30:00Z",
      "api_key_id": 5,
      "method": "GET",
      "path": "/api/users/123",
      "target_service": "users-service",
      "status_code": 200,
      "latency_ms": 45
    },
    {
      "id": 41,
      "timestamp": "2026-01-01T12:29:55Z",
      "api_key_id": 5,
      "method": "GET",
      "path": "/api/users",
      "target_service": "users-service",
      "status_code": 200,
      "latency_ms": 38
    }
  ],
  "total": 2
}
```

---

## 15. REQ-LOG-002: Configurable log levels

**Phase:** 3

**Depends on:** REQ-LOG-001

*Control log verbosity for different environments*

### Acceptance Criteria

1. The gateway supports four log levels in order of increasing severity: debug, info, warn, error.
2. Setting the log level to "info" suppresses debug-level messages but emits info, warn, and error messages.
3. Setting the log level to "debug" emits all messages including debug-level entries.
4. Setting the log level to "error" suppresses debug, info, and warn messages.
5. The default log level is "info" when no configuration is specified.
6. The log level can be set via the gateway YAML configuration file under `gateway.log_level`.
7. The log level can be overridden via an environment variable (e.g., GATEWAY_LOG_LEVEL).
8. An invalid log level value in configuration causes the gateway to log a warning and fall back to "info".
9. Debug-level logs include route matching decisions, cache hit/miss details, and circuit breaker state transitions.
10. The current log level is included in the GET /health response for operational visibility.

### API

### Configuration

```yaml
gateway:
  port: 8080
  log_level: debug
```

### GET /health (with log level)

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "uptime_seconds": 3600,
  "log_level": "debug"
}
```

---

## 16. REQ-RATE-002: Rate limit response headers

**Phase:** 3

**Depends on:** REQ-RATE-001

*Client visibility into rate limit state*

### Acceptance Criteria

1. Every authenticated response includes an X-RateLimit-Remaining header with the number of requests remaining in the current window.
2. Every authenticated response includes an X-RateLimit-Reset header with the Unix timestamp when the current window resets.
3. When the rate limit is exceeded, the 429 response also includes both rate limit headers.
4. The X-RateLimit-Remaining value is 0 when the rate limit has been exceeded.
5. An X-RateLimit-Limit header is included showing the applicable limit for the request.
6. The headers reflect the effective limit (considering per-key override and per-route config).
7. Unauthenticated responses (401) do not include rate limit headers.

### API

### Normal response with rate limit headers

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response headers:**
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1737020460
```

### Rate limit exceeded response

**Response headers:**
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1737020460
```

---

## 17. REQ-METRICS-001: Per-service and per-route request metrics

**Phase:** 8

**Depends on:** REQ-AUDIT-001

*Operational dashboard data*

### Acceptance Criteria

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

### API

Not applicable. Metrics are exposed through REQ-METRICS-002 (metrics admin endpoint). This requirement defines the internal counters and tracking logic.

### Internal counter structure

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

---

## 18. REQ-TRANSFORM-001: Request transformation before proxying

**Phase:** 4

**Depends on:** REQ-ROUTE-002, REQ-RATE-002

*Prepares requests for backend services*

### Acceptance Criteria

1. When strip_prefix is true, the matched route prefix is removed from the path before forwarding (e.g., `/api/users/123` with route `/api/users/*` becomes `/123`).
2. When strip_prefix is false, the full original path is forwarded unchanged.
3. An X-Request-ID header with a UUID v4 value is added to every proxied request.
4. An X-Forwarded-For header is added with the client's IP address.
5. An X-Forwarded-Host header is added with the original Host header value.
6. The original HTTP method is preserved in the proxied request.
7. The original request body is forwarded without modification.
8. The original query parameters are forwarded without modification.
9. Per-route custom headers defined in middleware_config.headers are injected into the proxied request.
10. If the backend request already has an X-Request-ID, the gateway's value takes precedence.
11. The X-Request-ID is stored in the request context for use in logging and audit.

### API

### Proxied request transformation

**Original request:**
```
GET /api/users/123?include=profile HTTP/1.1
Host: gateway.example.com
X-API-Key: sk_test_abc123
```

**Forwarded request (strip_prefix = true, route = /api/users/*):**
```
GET /123?include=profile HTTP/1.1
Host: localhost:3001
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Forwarded-For: 192.168.1.100
X-Forwarded-Host: gateway.example.com
```

---

## 19. REQ-TRANSFORM-002: Response transformation after proxying

**Phase:** 4

**Depends on:** REQ-TRANSFORM-001

*Post-processing of backend responses*

### Acceptance Criteria

1. An X-Gateway header with the gateway identifier is added to every proxied response.
2. An X-Request-ID header matching the request's correlation ID is added to the response.
3. An X-Response-Time header with the backend latency in milliseconds is added to the response.
4. An X-Cache header is added with value HIT or MISS indicating whether the response was served from cache.
5. The backend's original response status code is preserved.
6. The backend's original response body is forwarded without modification.
7. The backend's original response headers are forwarded, with gateway headers taking precedence on conflicts.
8. When the circuit breaker rejects a request (503), the response still includes X-Request-ID and X-Gateway headers.

### API

### Proxied response with gateway headers

**Backend response:**
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice"}
```

**Gateway response to client:**
```
HTTP/1.1 200 OK
Content-Type: application/json
X-Gateway: microservice-gateway
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 45ms
X-Cache: MISS

{"id": 123, "name": "Alice"}
```

---

## 20. REQ-CACHE-001: Response caching with configurable TTL

**Phase:** 5

**Depends on:** REQ-TRANSFORM-002

*Reduces backend load for cacheable responses*

### Acceptance Criteria

1. GET requests to cacheable routes with 200 responses are stored in the cache.
2. The cache key is composed of the HTTP method, request path, and alphabetically sorted query parameters.
3. A subsequent identical GET request within the TTL returns the cached response without calling the backend.
4. Cached responses include the original status code, response body, and response headers.
5. Cache entries expire after the configured cache_ttl_seconds has elapsed.
6. After TTL expiration, the next request fetches from the backend and re-populates the cache.
7. Non-GET requests (POST, PUT, DELETE, PATCH) are never cached.
8. Responses with non-200 status codes are never cached.
9. Routes with cache_ttl_seconds absent or set to 0 in middleware_config bypass the cache entirely.
10. Cache state is stored in memory and does not persist across gateway restarts.
11. A cached response sets X-Cache: HIT in the response headers.
12. A non-cached response sets X-Cache: MISS in the response headers.

### API

### Cache miss (first request)

**Request:**
```
GET /api/users?page=1&sort=name HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (200, X-Cache: MISS):**
```json
{
  "users": [{"id": 1, "name": "Alice"}],
  "total": 1
}
```

### Cache hit (subsequent request within TTL)

**Request:**
```
GET /api/users?sort=name&page=1 HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (200, X-Cache: HIT):**
```json
{
  "users": [{"id": 1, "name": "Alice"}],
  "total": 1
}
```

Note: The query parameters are sorted, so `?page=1&sort=name` and `?sort=name&page=1` produce the same cache key.

---

## 21. REQ-CACHE-002: Cache bypass and invalidation

**Phase:** 5

**Depends on:** REQ-CACHE-001

*Client control over caching behavior*

### Acceptance Criteria

1. A request with Cache-Control: no-cache header bypasses the cache and fetches from the backend.
2. A cache-bypassed request still stores the fresh response in the cache, replacing any existing entry.
3. The X-Cache header is set to MISS when Cache-Control: no-cache is used, even if a cached entry existed.
4. POST, PUT, and DELETE requests to a path invalidate any cached entry for that path.
5. The cache can be cleared entirely via DELETE /admin/cache with admin authentication.
6. DELETE /admin/cache returns 204 on success with the count of cleared entries.
7. Cache entries for a specific service can be invalidated via DELETE /admin/cache/:service_name.
8. The X-Cache header value is HIT only when the response is served directly from cache without contacting the backend.

### API

### Cache bypass request

**Request:**
```
GET /api/users HTTP/1.1
X-API-Key: sk_test_abc123
Cache-Control: no-cache
```

**Response (200):**
```
X-Cache: MISS
Content-Type: application/json

{"users": [{"id": 1, "name": "Alice"}]}
```

### Clear all cache entries

**Request:**
```
DELETE /admin/cache HTTP/1.1
X-API-Key: sk_admin_key
```

**Response (204):**
```json
{
  "cleared": 42
}
```

---

## 22. REQ-CIRCUIT-001: Circuit breaker with state machine

**Phase:** 6

**Depends on:** REQ-CACHE-002

*Prevents cascading failures to unhealthy backends*

### Acceptance Criteria

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

### API

### Circuit breaker open response

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (503 Service Unavailable):**
```json
{
  "error": "service unavailable",
  "service": "users-service",
  "circuit_state": "open",
  "retry_after_seconds": 30
}
```

---

## 23. REQ-CIRCUIT-002: Circuit breaker admin endpoints

**Phase:** 6

**Depends on:** REQ-CIRCUIT-001

*Operational visibility and manual recovery*

### Acceptance Criteria

1. GET /admin/circuit-breakers returns 200 with the current state of all circuit breakers.
2. Each circuit breaker entry includes service_id, service_name, state, failure_count, last_failure timestamp, and opened_at timestamp.
3. GET /admin/circuit-breakers returns an empty array when no services are registered.
4. POST /admin/circuit-breakers/:service_id/reset transitions the circuit breaker to closed and resets failure_count to 0.
5. POST /admin/circuit-breakers/:service_id/reset returns 200 with the updated circuit breaker state.
6. POST /admin/circuit-breakers/:service_id/reset returns 404 when the service_id does not exist.
7. Resetting a circuit breaker that is already closed returns 200 with no state change.
8. Both endpoints require admin role authentication.

### API

### GET /admin/circuit-breakers

**Response (200 OK):**
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

**Response (200 OK):**
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

---

## 24. REQ-RETRY-001: Retry with exponential backoff

**Phase:** 7

**Depends on:** REQ-CIRCUIT-001

*Resilience against transient backend failures*

### Acceptance Criteria

1. When a backend returns 502, 503, or 504, the gateway retries the request up to max_retries times.
2. Retry delay follows exponential backoff: 100ms for the first retry, 200ms for the second, 400ms for the third, and so on.
3. A route with max_retries set to 0 or absent in middleware_config does not retry failed requests.
4. GET and HEAD requests are retried by default when the route has max_retries configured.
5. POST, PATCH, and DELETE requests are not retried by default.
6. POST, PATCH, and DELETE can be retried if middleware_config includes retry_non_idempotent: true.
7. Each failed retry attempt counts as a failure for the circuit breaker.
8. If all retries are exhausted, the last error response from the backend is returned to the client.
9. The total request time includes all retry delays; if the route timeout_ms is exceeded during retries, remaining retries are abandoned.
10. Successful retry responses (2xx) are returned to the client normally and count as a circuit breaker success.
11. A 4xx response from the backend is not retried, regardless of the retry configuration.

### API

### Retry exhausted response

**Request:**
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

**Response (after 2 retries, all returning 503):**
```
HTTP/1.1 503 Service Unavailable
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Retry-Count: 2

{
  "error": "service unavailable after 2 retries"
}
```

### Successful retry

**Response (backend returned 503 on first attempt, 200 on retry):**
```
HTTP/1.1 200 OK
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Retry-Count: 1

{"id": 123, "name": "Alice"}
```

---

## 25. REQ-RETRY-002: Retry safety for non-idempotent methods

**Phase:** 7

**Depends on:** REQ-RETRY-001

*Prevents duplicate side effects from retries*

### Acceptance Criteria

1. GET, HEAD, OPTIONS, and PUT requests are retried automatically according to the route retry policy.
2. POST requests are NOT retried by default when the backend returns 502, 503, or 504.
3. PATCH requests are NOT retried by default when the backend returns 502, 503, or 504.
4. DELETE requests are NOT retried by default when the backend returns 502, 503, or 504.
5. When a route middleware_config includes `retry_non_idempotent: true`, POST/PATCH/DELETE requests are retried according to the normal retry policy.
6. When retry_non_idempotent is false or absent, non-idempotent methods return the original error response immediately without retrying.
7. The retry safety check occurs before the exponential backoff calculation to avoid unnecessary delay.
8. Circuit breaker failure counts still increment on the initial failed request even when retries are suppressed.
9. Audit log entries for non-retried failures record retry_count as 0.
10. The gateway logs a debug-level message when a retry is suppressed due to method safety.

### API

### Route configuration with retry safety override

**PUT /admin/routes/:id**

**Request:**
```json
{
  "path_pattern": "/api/orders/*",
  "method": "POST",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "max_retries": 2,
    "retry_non_idempotent": true
  }
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "path_pattern": "/api/orders/*",
  "method": "POST",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "max_retries": 2,
    "retry_non_idempotent": true
  },
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## 26. REQ-HEALTH-002: Background health checker for backend services

**Phase:** 8

**Depends on:** REQ-RETRY-002, REQ-HEALTH-001

*Proactive unhealthy service detection*

### Acceptance Criteria

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

### API

Not applicable. This is a background process. Health check results are visible through:

### GET /health/services

**Response (200 OK):**
```json
[
  {
    "name": "users-service",
    "is_healthy": true,
    "last_health_check": "2026-01-01T00:01:00Z"
  }
]
```

### GET /admin/services

**Response (200 OK):**
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

---

## 27. REQ-METRICS-002: Metrics admin endpoint

**Phase:** 8

**Depends on:** REQ-METRICS-001, REQ-HEALTH-002

*Admin access to operational metrics*

### Acceptance Criteria

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

### API

### GET /admin/metrics

**Request Headers:**
```
X-API-Key: admin-key-value
```

**Response (200 OK):**
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

---

## 28. REQ-CONFIG-002: Configuration hot-reload

**Phase:** 9

**Depends on:** REQ-CONFIG-001, REQ-METRICS-002

*Zero-downtime configuration changes*

### Acceptance Criteria

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

### API

### POST /admin/config/reload

**Request Headers:**
```
X-API-Key: admin-key-value
```

**Response (200 OK):**
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

### POST /admin/config/reload (validation error)

**Response (400 Bad Request):**
```json
{
  "error": "validation_failed",
  "message": "Route '/api/payments/*' references undefined service 'payments-service'",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

---

## 29. REQ-TEST-001: Comprehensive test suite with mock backends

**Phase:** 10

**Depends on:** REQ-CIRCUIT-002, REQ-RETRY-002, REQ-CORS-002, REQ-LOG-002, REQ-HEALTH-002, REQ-METRICS-002, REQ-CONFIG-002, REQ-VALID-001

*Verification depends on test coverage*

### Acceptance Criteria

1. The test suite runs with a single command (e.g., `make test` or `pytest` or `go test ./...`) and exits with code 0 on success, non-zero on failure.
2. Mock backend services are started and stopped automatically within the test harness; no external processes are required.
3. Tests cover all admin API CRUD operations: service registry, route management, and API key management.
4. Tests cover API key authentication: valid key, invalid key, missing key, revoked key, and role-based access control.
5. Tests cover rate limiting: requests within limit succeed, requests exceeding limit receive 429, rate limit headers are present.
6. Tests cover circuit breaker: closed-to-open transition after failures, open state returns 503, half-open recovery, and manual reset.
7. Tests cover request transformation: prefix stripping, X-Request-ID header injection, X-Forwarded-For and X-Forwarded-Host headers.
8. Tests cover response caching: cache hit returns cached response with X-Cache: HIT, cache miss proxies to backend, Cache-Control: no-cache bypasses cache.
9. Tests cover retry logic: retries on 502/503/504 with exponential backoff for idempotent methods, no retry for POST/PATCH/DELETE by default.
10. Tests cover CORS: preflight OPTIONS returns correct headers, non-preflight responses include CORS headers, disallowed origins are rejected.
11. Tests cover health endpoints: GET /health returns 200, GET /health/services reports backend health status.
12. Tests cover input validation: all admin endpoints return 422 with descriptive errors for invalid input.

### API

Not applicable. This is a test infrastructure requirement.

### Example test structure

```
tests/
  test_service_registry.py
  test_route_management.py
  test_api_key_management.py
  test_auth_middleware.py
  test_rate_limiting.py
  test_circuit_breaker.py
  test_request_transform.py
  test_response_caching.py
  test_retry_policy.py
  test_cors.py
  test_health.py
  test_input_validation.py
  test_structured_logging.py
  test_metrics.py
  test_config.py
  conftest.py  # Mock backend fixtures
```

---
