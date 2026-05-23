# REQ-WEBHOOK-004: Webhook Delivery History

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Implement a webhook delivery history endpoint that allows organization admins to view past delivery attempts for each webhook. The history includes the event type, payload, HTTP status code, response body, timestamp, and retry count for each delivery attempt. This provides visibility into webhook health and aids in debugging integration issues.

## Acceptance Criteria

1. GET /orgs/:slug/webhooks/:id/deliveries returns a paginated list of delivery attempts for the specified webhook.
2. Deliveries are listed in reverse chronological order (newest first).
3. Each delivery record includes id, webhook_id, event_type, payload, status_code, response_body, delivered_at, and retry_count.
4. GET /orgs/:slug/webhooks/:id/deliveries supports page and per_page query parameters.
5. GET /orgs/:slug/webhooks/:id/deliveries returns 404 if the webhook does not exist or belongs to another organization.
6. GET /orgs/:slug/webhooks/:id/deliveries returns 403 if the authenticated user is not an owner or admin.
7. Successful deliveries (2xx status codes) and failed deliveries are both included in the history.
8. The response body field is truncated to 1024 characters to prevent excessive storage.

## API Endpoints

### GET /orgs/:slug/webhooks/:id/deliveries

**Request:**
```
GET /orgs/acme/webhooks/1/deliveries?page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "deliveries": [
    {
      "id": 15,
      "webhook_id": 1,
      "event_type": "resource.created",
      "payload": {
        "event_type": "resource.created",
        "timestamp": "2026-01-15T10:30:00Z",
        "org_id": 1,
        "data": {"id": 10, "name": "Report Q4"}
      },
      "status_code": 200,
      "response_body": "OK",
      "delivered_at": "2026-01-15T10:30:01Z",
      "retry_count": 0
    },
    {
      "id": 14,
      "webhook_id": 1,
      "event_type": "project.created",
      "payload": {
        "event_type": "project.created",
        "timestamp": "2026-01-14T09:00:00Z",
        "org_id": 1,
        "data": {"id": 5, "name": "New Project"}
      },
      "status_code": 500,
      "response_body": "Internal Server Error",
      "delivered_at": "2026-01-14T09:00:01Z",
      "retry_count": 2
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
}
```

**Error (404 Not Found):**
```json
{
  "error": "webhook not found"
}
```

## Dependencies

- REQ-WEBHOOK-003: Requires webhook retry mechanism to populate delivery history with retry attempts.
