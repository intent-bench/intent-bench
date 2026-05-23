# REQ-CACHE-002: Cache Control and Bypass

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement cache bypass and invalidation mechanisms that give clients control over caching behavior. Clients can bypass the cache using the Cache-Control: no-cache request header. The X-Cache response header indicates whether a response was served from cache or fetched fresh from the backend.

## Acceptance Criteria

1. A request with Cache-Control: no-cache header bypasses the cache and fetches from the backend.
2. A cache-bypassed request still stores the fresh response in the cache, replacing any existing entry.
3. The X-Cache header is set to MISS when Cache-Control: no-cache is used, even if a cached entry existed.
4. POST, PUT, and DELETE requests to a path invalidate any cached entry for that path.
5. The cache can be cleared entirely via DELETE /admin/cache with admin authentication.
6. DELETE /admin/cache returns 204 on success with the count of cleared entries.
7. Cache entries for a specific service can be invalidated via DELETE /admin/cache/:service_name.
8. The X-Cache header value is HIT only when the response is served directly from cache without contacting the backend.

## API Endpoints

### Cache bypass request

Request:
```
GET /api/users HTTP/1.1
X-API-Key: sk_test_abc123
Cache-Control: no-cache
```

Response (200):
```
X-Cache: MISS
Content-Type: application/json

{"users": [{"id": 1, "name": "Alice"}]}
```

### Clear all cache entries

Request:
```
DELETE /admin/cache HTTP/1.1
X-API-Key: sk_admin_key
```

Response (204):
```json
{
  "cleared": 42
}
```

## Dependencies

- REQ-CACHE-001: Response caching must be implemented before bypass and invalidation can function.
