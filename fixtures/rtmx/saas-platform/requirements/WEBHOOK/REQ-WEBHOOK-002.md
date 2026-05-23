# REQ-WEBHOOK-002: Webhook Event Delivery with HMAC Signing

## Status: MISSING
## Priority: P0
## Phase: 6

## Requirement

Implement webhook event delivery that sends HTTP POST requests to registered webhook URLs when subscribed events occur. Each delivery payload is signed with HMAC-SHA256 using the webhook's secret, allowing recipients to verify payload authenticity. The system records delivery attempts with status codes and response details for monitoring and debugging.

## Acceptance Criteria

1. When a subscribed event occurs, the system sends an HTTP POST to each active webhook registered for that event type.
2. The request body contains a JSON payload with event_type, timestamp, org_id, and event-specific data.
3. The payload is signed with HMAC-SHA256 using the webhook's secret key.
4. The signature is included in the X-Webhook-Signature header as sha256=<hex_digest>.
5. The delivery request includes a Content-Type: application/json header.
6. The delivery request includes an X-Webhook-Event header with the event type.
7. A delivery is considered successful if the endpoint returns a 2xx status code.
8. Each delivery attempt is recorded in the webhook_deliveries table with webhook_id, event_type, payload, status_code, response_body, and delivered_at.
9. Inactive webhooks (is_active=false) do not receive deliveries.
10. Webhook deliveries do not block the API response that triggered the event.
11. If the endpoint does not respond within 10 seconds, the delivery is marked as timed out with status_code 0.

## API Endpoints

### Webhook delivery payload format

**HTTP POST to webhook URL:**
```
POST https://example.com/webhook
Content-Type: application/json
X-Webhook-Event: project.created
X-Webhook-Signature: sha256=5d41402abc4b2a76b9719d911017c592
```

```json
{
  "event_type": "project.created",
  "timestamp": "2026-01-15T10:30:00Z",
  "org_id": 1,
  "data": {
    "id": 5,
    "name": "New Project",
    "description": "A newly created project",
    "created_at": "2026-01-15T10:30:00Z"
  }
}
```

### Signature verification (recipient side)

```
expected = HMAC-SHA256(webhook_secret, raw_request_body)
actual = X-Webhook-Signature header value (after "sha256=" prefix)
verify: constant_time_compare(expected, actual)
```

## Dependencies

- REQ-WEBHOOK-001: Requires webhook registration to define target URLs, subscribed events, and signing secrets.
