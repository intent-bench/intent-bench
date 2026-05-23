# REQ-RATE-001: Rate Limiting

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement per-key rate limiting using a sliding window algorithm. The default limit is 100 requests per minute per API key. Rate limits can be overridden per-key via rate_limit_override and per-route via middleware_config. When the limit is exceeded, the gateway rejects the request with 429 Too Many Requests.

## Acceptance Criteria

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

## API Endpoints

### Rate limit exceeded

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (429):
```json
{
  "error": "rate limit exceeded",
  "retry_after_seconds": 32
}
```

## Dependencies

- REQ-AUTH-002: Authentication must identify the API key before rate limiting can apply per-key limits.
