# REQ-CONFIG-001: YAML Configuration File Parsing

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Parse a YAML configuration file at gateway startup to define all gateway behavior including listening port, log level, registered services, route mappings with middleware settings, rate limit defaults, and circuit breaker thresholds. The configuration file is the primary mechanism for declaratively defining gateway topology and behavior without requiring admin API calls.

## Acceptance Criteria

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

## API Endpoints

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

### Export Running Configuration

**GET /admin/config**

Request Headers:
```
X-API-Key: admin-key-value
```

Response (200 OK):
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

## Dependencies

None. This is a foundational requirement that drives all gateway behavior.
