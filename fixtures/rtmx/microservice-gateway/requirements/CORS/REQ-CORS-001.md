# REQ-CORS-001: CORS Preflight Handling

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Handle CORS preflight (OPTIONS) requests at the gateway level before proxying, returning the appropriate Access-Control headers based on per-route middleware configuration. Preflight responses must not be forwarded to backend services and must respect the allowed_origins, allowed_methods, allowed_headers, and max_age settings defined in each route's CORS configuration.

## Acceptance Criteria

1. An OPTIONS request to a route with CORS middleware configured returns a 204 No Content response without proxying to the backend.
2. The preflight response includes the Access-Control-Allow-Origin header matching the request Origin if it is in the allowed_origins list.
3. The preflight response includes Access-Control-Allow-Methods listing the methods from the route CORS allowed_methods configuration.
4. The preflight response includes Access-Control-Allow-Headers listing the headers from the route CORS allowed_headers configuration.
5. The preflight response includes Access-Control-Max-Age set to the route CORS max_age value in seconds.
6. When allowed_origins is ["*"], the Access-Control-Allow-Origin header is set to "*".
7. When the request Origin is not in the allowed_origins list, the preflight response omits the Access-Control-Allow-Origin header and returns 204 with no CORS headers.
8. An OPTIONS request to a route without CORS middleware configured returns 404 or passes through the normal routing logic.
9. Preflight responses are not recorded in the audit log as proxied requests.
10. The gateway does not require API key authentication for OPTIONS preflight requests on CORS-enabled routes.

## API Endpoints

### Route with CORS Middleware Configuration

**POST /admin/routes**

Request:
```json
{
  "path_pattern": "/api/users/*",
  "method": "*",
  "service_id": 1,
  "strip_prefix": true,
  "timeout_ms": 5000,
  "middleware_config": {
    "cors": {
      "allowed_origins": ["https://example.com", "https://app.example.com"],
      "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
      "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"],
      "max_age": 3600
    }
  }
}
```

### Preflight Request/Response

**OPTIONS /api/users/123**

Request Headers:
```
Origin: https://example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type, X-API-Key
```

Response (204 No Content):
```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key
Access-Control-Max-Age: 3600
```

## Dependencies

- REQ-ROUTE-001: Route management must exist so CORS middleware configuration can be attached to routes.
