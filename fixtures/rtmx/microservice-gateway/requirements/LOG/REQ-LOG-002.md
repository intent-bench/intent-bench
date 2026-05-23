# REQ-LOG-002: Configurable Log Levels

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Support configurable log levels (debug, info, warn, error) to control log verbosity at runtime and through configuration. The log level determines which log entries are emitted, allowing operators to increase verbosity for debugging or reduce noise in production environments.

## Acceptance Criteria

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

## API Endpoints

### Configuration

```yaml
gateway:
  port: 8080
  log_level: debug
```

### Health Response with Log Level

**GET /health**

Response (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "uptime_seconds": 3600,
  "log_level": "debug"
}
```

## Dependencies

- REQ-LOG-001: Structured JSON logging must be implemented before log level filtering can be applied.
