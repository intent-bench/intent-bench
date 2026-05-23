# REQ-WEBHOOK-001: Webhook Registration and Management

## Status: MISSING
## Priority: P0
## Phase: 6

## Requirement

Implement webhook registration and management endpoints that allow organization admins to create, list, update, and delete webhooks scoped to their organization. Each webhook specifies a target URL, a list of event types to subscribe to, a secret for payload signing, and an active/inactive status. Webhook management is restricted to users with owner or admin roles.

## Acceptance Criteria

1. POST /orgs/:slug/webhooks creates a new webhook with url, events, secret, and is_active fields.
2. POST /orgs/:slug/webhooks auto-generates a cryptographically random secret if none is provided.
3. POST /orgs/:slug/webhooks returns 403 if the authenticated user is not an owner or admin.
4. POST /orgs/:slug/webhooks validates that the events array contains only recognized event types.
5. GET /orgs/:slug/webhooks returns a list of all webhooks for the organization.
6. GET /orgs/:slug/webhooks does not expose the webhook secret in list responses.
7. PUT /orgs/:slug/webhooks/:id updates the webhook url, events, or is_active status.
8. PUT /orgs/:slug/webhooks/:id allows regenerating the secret by passing a new value.
9. DELETE /orgs/:slug/webhooks/:id deletes the webhook and all associated delivery records.
10. Recognized event types are: member.joined, member.removed, project.created, project.archived, project.deleted, resource.created, resource.updated, resource.deleted.
11. All webhook CRUD operations are scoped to the current organization via tenant isolation.

## API Endpoints

### POST /orgs/:slug/webhooks

**Request:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["project.created", "resource.created", "resource.updated"],
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "url": "https://example.com/webhook",
  "events": ["project.created", "resource.created", "resource.updated"],
  "secret": "whsec_a1b2c3d4e5f6g7h8",
  "is_active": true,
  "created_at": "2026-01-15T10:30:00Z"
}
```

### GET /orgs/:slug/webhooks

**Response (200 OK):**
```json
{
  "webhooks": [
    {
      "id": 1,
      "org_id": 1,
      "url": "https://example.com/webhook",
      "events": ["project.created", "resource.created", "resource.updated"],
      "is_active": true,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

### DELETE /orgs/:slug/webhooks/:id

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

## Dependencies

- REQ-RBAC-002: Requires role-based access control middleware to enforce owner/admin permissions.
