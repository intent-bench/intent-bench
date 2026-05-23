# REQ-VALID-001: Input Validation

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement comprehensive input validation across all endpoints. Every endpoint must validate its input and return 422 Unprocessable Entity with descriptive error messages for invalid data. The system must also return appropriate HTTP status codes for authentication failures (401), authorization failures (403), missing resources (404), and uniqueness violations (409).

## Acceptance Criteria

1. Email fields must conform to a valid email format; invalid emails return 422 with a descriptive error.
2. Username must be 3-30 characters and contain only alphanumeric characters; violations return 422.
3. Password must be at least 8 characters; shorter passwords return 422.
4. Product name must be non-empty; empty names return 422.
5. Product price must be greater than 0; zero or negative prices return 422.
6. Product SKU must be non-empty; empty SKUs return 422.
7. Review rating must be an integer between 1 and 5 inclusive; out-of-range values return 422.
8. Discount code percent must be an integer between 1 and 100 inclusive; out-of-range values return 422.
9. Date fields must conform to ISO 8601 format; invalid dates return 422.
10. Quantity fields must be positive integers; zero or negative quantities return 422.
11. Requests without a valid authentication token return 401 Unauthorized.
12. Requests where the authenticated user lacks required permissions return 403 Forbidden.
13. Requests referencing a non-existent resource return 404 Not Found.
14. Requests that violate uniqueness constraints (duplicate email, username, SKU, review) return 409 Conflict.

## API Endpoints

### Error response format

All validation errors follow a consistent format.

**Error (422 Unprocessable Entity):**
```json
{
  "error": "validation failed",
  "details": [
    {
      "field": "email",
      "message": "invalid email format"
    },
    {
      "field": "password",
      "message": "password must be at least 8 characters"
    }
  ]
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
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
  "error": "email already registered"
}
```

## Dependencies

- REQ-DB-001: Requires database schema to define the constraints that validation enforces.
