# REQ-ROUTE-002: Path Pattern Matching

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement the request routing logic that matches incoming request paths against registered route patterns. The gateway must support wildcard path patterns, select the most specific matching route, and filter by HTTP method. Unmatched requests must return a 404 response.

## Acceptance Criteria

1. A route with path_pattern `/api/users/*` matches requests to `/api/users/123` and `/api/users/123/profile`.
2. A route with path_pattern `/api/users` (no wildcard) matches only the exact path `/api/users`.
3. When multiple routes match, the most specific pattern wins (e.g., `/api/users/admin` beats `/api/users/*`).
4. A route with method `*` matches all HTTP methods (GET, POST, PUT, DELETE, PATCH).
5. A route with method `GET` matches only GET requests; POST to the same path returns 404 if no other route matches.
6. A request to a path with no matching route returns 404 with a JSON error body.
7. Route matching is case-sensitive for path segments.
8. The matched route is passed to the middleware chain for processing.
9. A route with path_pattern `/api/v1/*` does not match `/api/v2/users`.
10. Trailing slashes are normalized so `/api/users/` and `/api/users` match the same route.

## API Endpoints

### Proxy request (matched route)

Request:
```
GET /api/users/123 HTTP/1.1
X-API-Key: sk_test_abc123
```

Response: Proxied from the backend service associated with the matching route.

### Proxy request (no matching route)

Request:
```
GET /unknown/path HTTP/1.1
X-API-Key: sk_test_abc123
```

Response (404):
```json
{
  "error": "no route matches path /unknown/path"
}
```

## Dependencies

- REQ-ROUTE-001: Routes must be created before matching can occur.
