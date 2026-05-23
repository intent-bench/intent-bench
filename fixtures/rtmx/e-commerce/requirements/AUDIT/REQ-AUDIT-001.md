# REQ-AUDIT-001: Audit Logging

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Implement an append-only audit log that records every create, update, and delete operation on products, orders, payments, shipments, reviews, and discount codes. Each audit log entry captures the acting user, the action performed, the entity type and ID, a JSON details field, and a timestamp. Administrators can query the log with filtering by entity type, user ID, and date range. Audit log entries cannot be updated or deleted.

## Acceptance Criteria

1. Every create operation on products, orders, payments, shipments, reviews, and discount codes creates an audit log entry.
2. Every update operation on the above entities creates an audit log entry.
3. Every delete operation on the above entities creates an audit log entry.
4. Each audit log entry contains user_id, action, entity_type, entity_id, details (JSON), and timestamp.
5. The action field is one of: "create", "update", "delete".
6. The details field contains a JSON representation of the relevant changes or entity state.
7. GET /admin/audit-log returns a paginated list of audit log entries (admin only).
8. GET /admin/audit-log supports filtering by entity_type query parameter.
9. GET /admin/audit-log supports filtering by user_id query parameter.
10. GET /admin/audit-log supports filtering by start_date and end_date query parameters (ISO 8601).
11. GET /admin/audit-log returns 403 if the authenticated user is not an admin.
12. Audit log entries are append-only: no PUT or DELETE endpoints exist for audit log entries.

## API Endpoints

### GET /admin/audit-log

**Request:**
```
GET /admin/audit-log?entity_type=product&user_id=2&start_date=2026-01-01T00:00:00Z&end_date=2026-01-31T23:59:59Z&page=1&per_page=20
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 42,
      "user_id": 2,
      "action": "create",
      "entity_type": "product",
      "entity_id": 3,
      "details": {
        "name": "Widget",
        "price": 39.99,
        "sku": "WDG-001"
      },
      "timestamp": "2026-01-10T08:00:00Z"
    },
    {
      "id": 45,
      "user_id": 2,
      "action": "update",
      "entity_type": "product",
      "entity_id": 3,
      "details": {
        "field": "price",
        "old_value": 39.99,
        "new_value": 34.99
      },
      "timestamp": "2026-01-15T09:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication to identify the acting user and enforce admin access.
