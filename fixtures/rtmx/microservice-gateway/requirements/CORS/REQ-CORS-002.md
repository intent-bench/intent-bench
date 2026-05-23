# REQ-CORS-002: CORS Response Headers

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Add Access-Control response headers to all non-preflight requests on routes with CORS middleware configured. The gateway must inject CORS headers into proxied responses so that browsers permit cross-origin access according to the per-route CORS policy, including support for credentialed requests and exposed headers.

## Acceptance Criteria

1. Non-OPTIONS requests to CORS-enabled routes include Access-Control-Allow-Origin in the response, matching the request Origin against the allowed_origins list.
2. When allowed_origins is ["*"], Access-Control-Allow-Origin is set to "*" on all responses.
3. When the request Origin is not in the allowed_origins list, no Access-Control-Allow-Origin header is added to the response.
4. The Vary: Origin header is included in responses when allowed_origins is not ["*"] to ensure correct caching behavior.
5. Access-Control-Expose-Headers is included in the response if expose_headers is configured in the route CORS middleware.
6. Access-Control-Allow-Credentials is set to "true" when allow_credentials is enabled in the route CORS middleware.
7. When allow_credentials is true, Access-Control-Allow-Origin must not be "*" but must echo the specific origin.
8. CORS headers are added after the backend response is received, during response transformation.
9. Routes without CORS middleware configured do not have any Access-Control headers added.

## API Endpoints

### Proxied Request with CORS Headers

**GET /api/users/123**

Request Headers:
```
Origin: https://example.com
X-API-Key: valid-service-key
```

Response (200 OK):
```
Access-Control-Allow-Origin: https://example.com
Vary: Origin
Content-Type: application/json

{"id": 123, "name": "Jane Doe"}
```

### Request from Disallowed Origin

**GET /api/users/123**

Request Headers:
```
Origin: https://evil.com
X-API-Key: valid-service-key
```

Response (200 OK):
```
Content-Type: application/json

{"id": 123, "name": "Jane Doe"}
```

No Access-Control-Allow-Origin header is present in the response.

## Dependencies

- REQ-CORS-001: Preflight handling must be implemented first; response header logic shares the same CORS configuration.
