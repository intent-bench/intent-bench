# REQ-AUDIT-001: Audit Logging for All Mutations

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement an append-only audit log that records every create, update, and delete operation across all tenant-scoped entities. Each audit log entry captures the acting user ID, the action performed, the entity type and ID, a JSON details field with relevant context, the client IP address, and a timestamp. Audit log entries are scoped to organizations and cannot be updated or deleted.

## Acceptance Criteria

1. Every create operation on organizations, members, projects, resources, API keys, webhooks, and billing records creates an audit log entry.
2. Every update operation on the above entities creates an audit log entry.
3. Every delete operation on the above entities creates an audit log entry.
4. Each audit log entry contains org_id, user_id, action, entity_type, entity_id, details (JSON), ip_address, and timestamp.
5. The action field is one of: "create", "update", "delete".
6. The details field contains a JSON representation of the relevant changes or entity state at the time of the action.
7. The ip_address field captures the client IP from the request.
8. Audit log entries are append-only: no PUT or DELETE endpoints exist for audit log entries.
9. Audit log entries are scoped to the organization in which the action occurred.
10. Audit logging does not block or slow the triggering API response beyond negligible overhead.
11. Role changes, invitation sends, and invitation acceptances are all recorded as audit events.

## API Endpoints

### Audit log entry format

Audit log entries are created automatically by the system. They are queried via the endpoint defined in REQ-AUDIT-002.

**Example audit log entry:**
```json
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
```

**Example role change audit entry:**
```json
{
  "id": 55,
  "org_id": 1,
  "user_id": 1,
  "action": "update",
  "entity_type": "membership",
  "entity_id": 3,
  "details": {
    "field": "role",
    "old_value": "member",
    "new_value": "admin"
  },
  "ip_address": "10.0.0.5",
  "timestamp": "2026-01-16T14:00:00Z"
}
```

## Dependencies

- REQ-RBAC-002: Requires role-based access control middleware to identify the acting user for audit entries.
