# REQ-TRANSFORM-001: Request Transformation

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement request transformation that modifies outgoing requests before they are proxied to backend services. The gateway must strip the route prefix when configured, add correlation and forwarding headers, and forward the original method, body, and query parameters. Per-route header injection is supported via middleware_config.

## Acceptance Criteria

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

## API Endpoints

### Proxied request transformation

Original request:
```
GET /api/users/123?include=profile HTTP/1.1
Host: gateway.example.com
X-API-Key: sk_test_abc123
```

Forwarded request (strip_prefix = true, route = /api/users/*):
```
GET /123?include=profile HTTP/1.1
Host: localhost:3001
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Forwarded-For: 192.168.1.100
X-Forwarded-Host: gateway.example.com
```

## Dependencies

- REQ-ROUTE-002: Route matching must resolve the matching route and its strip_prefix setting.
- REQ-RATE-002: Rate limit headers are added before request transformation occurs in the chain.
