# API Gateway

Build a complete API gateway from scratch in this empty project directory. The gateway acts as a reverse proxy that routes incoming HTTP requests to backend services, applying middleware (authentication, rate limiting, caching, circuit breaking) along the way.

## Core Concepts

- **Services**: Backend HTTP servers registered with the gateway (name, URL, health check path)
- **Routes**: URL path patterns mapped to services with middleware configuration
- **Middleware Chain**: Ordered pipeline of request/response processors applied per-route
- **Circuit Breaker**: Monitors backend failures and short-circuits requests when a service is unhealthy
- **Config**: YAML-based configuration with hot-reload support

## Data Model

- **Services**: id, name, base_url, health_check_path, is_healthy, last_health_check, created_at
- **Routes**: id, path_pattern, method, service_id, strip_prefix, timeout_ms, middleware_config (JSON), created_at
- **API Keys**: id, key_hash, name, role (admin|service), rate_limit_override, is_active, created_at
- **Rate Limit Entries**: key, window_start, request_count (in-memory or SQLite)
- **Circuit Breaker State**: service_id, state (closed|open|half_open), failure_count, last_failure, opened_at
- **Cache Entries**: cache_key, response_body, response_headers, status_code, cached_at, ttl_seconds
- **Audit Log**: id, timestamp, api_key_id, method, path, target_service, status_code, latency_ms

## Admin API (all require admin API key)

### Service Registry
- POST /admin/services -- Register a new backend service
- GET /admin/services -- List all registered services with health status
- GET /admin/services/:id -- Get service details
- PUT /admin/services/:id -- Update service configuration
- DELETE /admin/services/:id -- Deregister a service

### Route Management
- POST /admin/routes -- Create a route mapping (path pattern -> service + middleware)
- GET /admin/routes -- List all routes
- PUT /admin/routes/:id -- Update route configuration
- DELETE /admin/routes/:id -- Delete a route

### API Key Management
- POST /admin/keys -- Create an API key (returns the key once, stores hash)
- GET /admin/keys -- List API keys (without key values)
- DELETE /admin/keys/:id -- Revoke an API key

### Monitoring
- GET /admin/metrics -- Request counts, latencies, error rates per service
- GET /admin/circuit-breakers -- Current state of all circuit breakers
- POST /admin/circuit-breakers/:service_id/reset -- Manually reset a circuit breaker
- GET /admin/audit-log -- Query audit log with filters (?service=&method=&from=&to=)

### Configuration
- POST /admin/config/reload -- Hot-reload configuration from YAML file
- GET /admin/config -- Export current running configuration

## Gateway Proxy Behavior

### Request Flow
1. Incoming request hits the gateway
2. Route matching: find the route whose path_pattern matches the request path
3. API key authentication: validate the X-API-Key header
4. Rate limiting: check request count against limits
5. Request transformation: modify headers, strip prefix, add correlation ID
6. Cache check: return cached response if available (GET only)
7. Circuit breaker check: reject if backend circuit is open
8. Proxy request to backend service (with timeout)
9. Circuit breaker update: record success/failure
10. Response transformation: add gateway headers
11. Cache store: cache successful GET responses if cacheable
12. Audit log: record request details

### Route Matching
- Routes use path patterns: `/api/users/*` matches `/api/users/123`
- Most specific pattern wins
- If no route matches, return 404
- Method matching: route can specify GET, POST, etc. or * for all methods

### Authentication
- All proxy requests require an X-API-Key header
- Admin API requires a key with role "admin"
- Service keys have role "service" (proxy access only)
- Invalid or missing key returns 401
- Revoked key returns 403

### Rate Limiting
- Default: 100 requests per minute per API key
- Configurable per-key via rate_limit_override
- Configurable per-route via middleware_config
- Sliding window algorithm
- Return 429 Too Many Requests when exceeded
- Include X-RateLimit-Remaining and X-RateLimit-Reset headers

### Circuit Breaker
- Per-service circuit breaker (not per-route)
- States: closed (normal), open (rejecting), half_open (testing)
- Closed -> Open: after 5 consecutive failures (configurable)
- Open -> Half Open: after 30 seconds (configurable)
- Half Open -> Closed: on first success
- Half Open -> Open: on first failure
- When open, return 503 Service Unavailable without calling backend
- Record failure_count and state transitions

### Request Transformation
- Strip route prefix before forwarding (if strip_prefix is true)
- Add X-Request-ID header (UUID) to all proxied requests
- Add X-Forwarded-For, X-Forwarded-Host headers
- Forward original method, body, and query parameters
- Configurable header injection per-route (via middleware_config)

### Response Caching
- Cache GET responses with status 200 for configurable TTL
- Cache key: method + path + sorted query parameters
- Cacheable routes configured via middleware_config (cache_ttl_seconds)
- Non-cacheable routes (cache_ttl_seconds = 0 or absent) bypass cache
- Cache-Control: no-cache header in request bypasses cache
- Add X-Cache: HIT or X-Cache: MISS header to responses

### Retry Policy
- Configurable retries per-route (via middleware_config: max_retries)
- Retry on 502, 503, 504 responses
- Exponential backoff: 100ms, 200ms, 400ms...
- Do not retry non-idempotent methods (POST, PATCH, DELETE) unless explicitly configured
- Circuit breaker failures count across retries

### CORS
- Configurable per-route via middleware_config
- Support: allowed_origins, allowed_methods, allowed_headers, max_age
- Preflight (OPTIONS) handling
- Default: deny all cross-origin requests

### Health Checks
- GET /health -- Gateway health (always 200 if gateway is running)
- GET /health/services -- Aggregate health of all registered services
- Background health checker: polls each service's health_check_path every 30 seconds
- Updates is_healthy and last_health_check on each poll
- Unhealthy services trigger circuit breaker state changes

### Structured Logging
- All proxy requests logged with: timestamp, request_id, method, path, service, status_code, latency_ms
- Log level configurable (debug, info, warn, error)
- Errors include stack context
- JSON format for machine parsing

### Metrics
- Per-service: total requests, success count, error count, avg latency, p99 latency
- Per-route: request count, cache hit rate
- Global: total requests, active connections
- Computed from audit log and in-memory counters

## Configuration File Format

```yaml
gateway:
  port: 8080
  log_level: info

services:
  - name: users-service
    base_url: http://localhost:3001
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

## Requirements Summary

1. API key authentication with role-based access (admin vs service)
2. Rate limiting with sliding window and per-key/per-route overrides
3. Circuit breaker pattern with configurable thresholds
4. Request/response transformation (headers, prefix stripping, correlation IDs)
5. Response caching with TTL and cache-control support
6. Retry with exponential backoff for failed requests
7. CORS support configurable per-route
8. Background health checks for registered services
9. Structured JSON logging for all requests
10. Metrics aggregation (per-service, per-route, global)
11. YAML configuration with hot-reload
12. Audit log for all proxied requests
13. Return 401 for missing/invalid API keys
14. Return 403 for revoked keys or insufficient role
15. Return 404 for unmatched routes
16. Return 429 for rate limit exceeded
17. Return 503 when circuit breaker is open

## Technical Constraints

- The gateway should listen on port 8080 by default
- You may use any programming language and framework
- Use SQLite for persistent storage (services, routes, keys, audit log)
- In-memory storage is acceptable for rate limits, circuit breaker state, and cache
- Include a comprehensive test suite that can be run with a single command
- Tests should cover all middleware behaviors, admin API, and proxy functionality
- The test suite should be self-contained (mock backend services, not real ones)
