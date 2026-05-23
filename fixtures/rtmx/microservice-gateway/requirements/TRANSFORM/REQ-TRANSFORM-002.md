# REQ-TRANSFORM-002: Response Transformation

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Implement response transformation that modifies responses received from backend services before returning them to the client. The gateway must add gateway identification headers and an X-Cache header indicating cache hit or miss status. The original response body and status code from the backend are preserved.

## Acceptance Criteria

1. An X-Gateway header with the gateway identifier is added to every proxied response.
2. An X-Request-ID header matching the request's correlation ID is added to the response.
3. An X-Response-Time header with the backend latency in milliseconds is added to the response.
4. An X-Cache header is added with value HIT or MISS indicating whether the response was served from cache.
5. The backend's original response status code is preserved.
6. The backend's original response body is forwarded without modification.
7. The backend's original response headers are forwarded, with gateway headers taking precedence on conflicts.
8. When the circuit breaker rejects a request (503), the response still includes X-Request-ID and X-Gateway headers.

## API Endpoints

### Proxied response with gateway headers

Backend response:
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice"}
```

Gateway response to client:
```
HTTP/1.1 200 OK
Content-Type: application/json
X-Gateway: microservice-gateway
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 45ms
X-Cache: MISS

{"id": 123, "name": "Alice"}
```

## Dependencies

- REQ-TRANSFORM-001: Request transformation must have added X-Request-ID to the context before response transformation can include it.
