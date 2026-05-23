# REQ-VALID-001: Input Validation

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement comprehensive input validation across all API endpoints. Every endpoint must validate its input and return 422 Unprocessable Entity with descriptive field-level error messages for invalid data. Validation covers required fields, format constraints, length limits, and type checks for all entities in the platform.

## Acceptance Criteria

1. Email fields must conform to a valid email format; invalid emails return 422 with a descriptive field-level error.
2. Username must be 3-30 characters and contain only alphanumeric characters; violations return 422.
3. Password must be at least 8 characters; shorter passwords return 422.
4. Organization name must be non-empty and at most 100 characters; violations return 422.
5. Organization slug must be 3-50 characters, lowercase alphanumeric with hyphens only; violations return 422.
6. Project name must be non-empty and at most 200 characters; violations return 422.
7. Resource name must be non-empty; empty names return 422.
8. Resource type must be non-empty; empty types return 422.
9. Resource metadata must be valid JSON if provided; invalid JSON returns 422.
10. Webhook URL must be a valid HTTPS URL; invalid URLs return 422.
11. API key scopes must be a non-empty array containing only recognized values (read, write, admin); violations return 422.
12. Date fields must conform to ISO 8601 format; invalid dates return 422.

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

**Error (422 Unprocessable Entity -- single field):**
```json
{
  "error": "validation failed",
  "details": [
    {
      "field": "slug",
      "message": "slug must be 3-50 lowercase alphanumeric characters or hyphens"
    }
  ]
}
```

## Dependencies

- REQ-DB-001: Requires database schema to define the constraints that validation enforces.
