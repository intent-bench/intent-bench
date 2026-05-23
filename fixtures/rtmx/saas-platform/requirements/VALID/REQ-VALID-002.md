# REQ-VALID-002: Consistent Error Response Format

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement a consistent error response format across all API endpoints for all HTTP error status codes. Every error response must return a JSON object with an error field containing a human-readable message. The system must use the correct HTTP status codes: 401 for authentication failures, 402 for quota/billing limit violations, 403 for authorization failures, 404 for missing resources or wrong tenant, 409 for uniqueness violations, and 422 for validation errors.

## Acceptance Criteria

1. All error responses return a JSON object with at minimum an "error" field containing a descriptive message.
2. 401 Unauthorized is returned when no authentication token is provided or the token is invalid/expired.
3. 402 Payment Required is returned when an operation would exceed the organization's plan limits.
4. 403 Forbidden is returned when the authenticated user lacks the required role or permission for the operation.
5. 404 Not Found is returned when the requested resource does not exist or belongs to a different tenant.
6. 409 Conflict is returned when an operation violates a uniqueness constraint (duplicate email, username, slug, etc.).
7. 422 Unprocessable Entity is returned for validation errors and includes a details array with field-level messages.
8. 400 Bad Request is returned for malformed requests or missing required query parameters.
9. 500 Internal Server Error responses include a generic error message and never expose internal implementation details.
10. All error responses include the Content-Type: application/json header.

## API Endpoints

### Standard error response formats

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
}
```

**Error (402 Payment Required):**
```json
{
  "error": "plan limit exceeded: upgrade to add more projects"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions"
}
```

**Error (404 Not Found):**
```json
{
  "error": "resource not found"
}
```

**Error (409 Conflict):**
```json
{
  "error": "slug already in use"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "validation failed",
  "details": [
    {
      "field": "name",
      "message": "name is required"
    }
  ]
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "internal server error"
}
```

## Dependencies

- REQ-VALID-001: Requires input validation to generate the field-level error details for 422 responses.
