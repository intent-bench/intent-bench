# REQ-AUDIT-002: Audit Log Querying with Filters

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Implement an audit log query endpoint that allows organization admins to search and filter audit log entries within their organization. The endpoint supports filtering by entity type, user ID, action, and date range, with pagination. This enables compliance reporting, incident investigation, and security monitoring within the organization boundary.

## Acceptance Criteria

1. GET /orgs/:slug/audit-log returns a paginated list of audit log entries for the organization, newest first.
2. GET /orgs/:slug/audit-log supports filtering by entity_type query parameter (e.g., project, resource, membership).
3. GET /orgs/:slug/audit-log supports filtering by user_id query parameter.
4. GET /orgs/:slug/audit-log supports filtering by action query parameter (create, update, delete).
5. GET /orgs/:slug/audit-log supports filtering by start_date and end_date query parameters in ISO 8601 format.
6. GET /orgs/:slug/audit-log supports page and per_page query parameters with defaults of page=1 and per_page=20.
7. GET /orgs/:slug/audit-log returns 403 if the authenticated user is not an owner or admin of the organization.
8. Results are scoped to the current organization; no cross-tenant audit data is accessible.
9. Multiple filters can be combined in a single query (e.g., entity_type=project AND user_id=5 AND action=delete).
10. The total count of matching entries is returned in the response for pagination.

## API Endpoints

### GET /orgs/:slug/audit-log

**Request:**
```
GET /orgs/acme/audit-log?entity_type=project&user_id=2&action=create&start_date=2026-01-01T00:00:00Z&end_date=2026-01-31T23:59:59Z&page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 42,
      "org_id": 1,
      "user_id": 2,
      "action": "create",
      "entity_type": "project",
      "entity_id": 5,
      "details": {
        "name": "Q4 Report",
        "description": "Quarterly analysis project"
      },
      "ip_address": "192.168.1.100",
      "timestamp": "2026-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

## Dependencies

- REQ-AUDIT-001: Requires audit logging infrastructure to populate the audit log entries that this endpoint queries.
