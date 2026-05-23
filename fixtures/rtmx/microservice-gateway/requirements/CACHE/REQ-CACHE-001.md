# REQ-CACHE-001: Response Caching

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement in-memory response caching for GET requests that return 200 status codes. Cache entries are keyed by method, path, and sorted query parameters. Caching is enabled per-route via the cache_ttl_seconds field in middleware_config. Routes without cache_ttl_seconds or with a value of 0 bypass caching entirely.

## Acceptance Criteria

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

## API Endpoints

### Cache miss (first request)

Request:
```
GET /api/users?page=1&sort=name HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (200, X-Cache: MISS):
```json
{
  "users": [{"id": 1, "name": "Alice"}],
  "total": 1
}
```

### Cache hit (subsequent request within TTL)

Request:
```
GET /api/users?sort=name&page=1 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (200, X-Cache: HIT):
```json
{
  "users": [{"id": 1, "name": "Alice"}],
  "total": 1
}
```

Note: The query parameters are sorted, so `?page=1&sort=name` and `?sort=name&page=1` produce the same cache key.

## Dependencies

- REQ-TRANSFORM-002: Response transformation must add the X-Cache header to responses.
