# REQ-RATE-002: Rate Limit Headers

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Include rate limit information in response headers so clients have visibility into their current rate limit state. Every response to an authenticated request must include X-RateLimit-Remaining and X-RateLimit-Reset headers, regardless of whether the rate limit has been exceeded.

## Acceptance Criteria

1. Every authenticated response includes an X-RateLimit-Remaining header with the number of requests remaining in the current window.
2. Every authenticated response includes an X-RateLimit-Reset header with the Unix timestamp when the current window resets.
3. When the rate limit is exceeded, the 429 response also includes both rate limit headers.
4. The X-RateLimit-Remaining value is 0 when the rate limit has been exceeded.
5. An X-RateLimit-Limit header is included showing the applicable limit for the request.
6. The headers reflect the effective limit (considering per-key override and per-route config).
7. Unauthenticated responses (401) do not include rate limit headers.

## API Endpoints

### Normal response with rate limit headers

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response headers:
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1737020460
```

### Rate limit exceeded response

Response headers:
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1737020460
```

## Dependencies

- REQ-RATE-001: Rate limiting logic must exist before headers can report its state.
