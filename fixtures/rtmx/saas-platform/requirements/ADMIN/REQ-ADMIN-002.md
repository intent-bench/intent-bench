# REQ-ADMIN-002: Platform Admin Audit Log Access

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement a platform admin endpoint that provides cross-organization audit log access for compliance investigations and security monitoring. Platform admins can view the audit log of any organization without being a member, using the same filtering capabilities as the organization-level audit log. This enables platform-wide compliance oversight and incident response.

## Acceptance Criteria

1. GET /admin/orgs/:slug/audit-log returns a paginated list of audit log entries for the specified organization.
2. GET /admin/orgs/:slug/audit-log supports filtering by entity_type, user_id, action, start_date, and end_date query parameters.
3. GET /admin/orgs/:slug/audit-log supports page and per_page query parameters.
4. GET /admin/orgs/:slug/audit-log returns 403 if the authenticated user does not have is_platform_admin=true.
5. GET /admin/orgs/:slug/audit-log returns 404 if the specified organization slug does not exist.
6. Platform admins can access audit logs for any organization regardless of membership.
7. The response format is identical to the organization-level audit log endpoint (GET /orgs/:slug/audit-log).
8. Platform admin audit log access is itself recorded in the audit log with a distinct entity_type of "admin_access".

## API Endpoints

### GET /admin/orgs/:slug/audit-log

**Request:**
```
GET /admin/orgs/acme/audit-log?entity_type=membership&action=delete&page=1&per_page=20
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 120,
      "org_id": 1,
      "user_id": 1,
      "action": "delete",
      "entity_type": "membership",
      "entity_id": 7,
      "details": {
        "removed_user_id": 7,
        "removed_role": "member"
      },
      "ip_address": "10.0.0.5",
      "timestamp": "2026-01-14T16:00:00Z"
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
  "error": "platform admin access required"
}
```

## Dependencies

- REQ-ADMIN-001: Requires platform admin console for admin authentication and authorization.
- REQ-AUDIT-002: Requires audit log querying infrastructure for the filtering and pagination logic.
