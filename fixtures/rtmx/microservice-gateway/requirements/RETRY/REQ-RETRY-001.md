# REQ-RETRY-001: Retry with Exponential Backoff

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Implement a configurable retry policy with exponential backoff for failed proxy requests. Retries are configured per-route via the max_retries field in middleware_config. The gateway retries on 502, 503, and 504 responses from backends. Non-idempotent methods (POST, PATCH, DELETE) are not retried by default to prevent duplicate side effects.

## Acceptance Criteria

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

## API Endpoints

### Retry exhausted response

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (after 2 retries, all returning 503):
```
HTTP/1.1 503 Service Unavailable
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Retry-Count: 2

{
  "error": "service unavailable after 2 retries"
}
```

### Successful retry

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (backend returned 503 on first attempt, 200 on retry):
```
HTTP/1.1 200 OK
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Retry-Count: 1

{"id": 123, "name": "Alice"}
```

## Dependencies

- REQ-CIRCUIT-001: Circuit breaker state must be checked before each retry attempt; retry failures count toward the circuit breaker threshold.
