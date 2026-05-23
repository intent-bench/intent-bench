# REQ-WEBHOOK-003: Webhook Retry with Exponential Backoff

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Implement a retry mechanism for failed webhook deliveries using exponential backoff. When a webhook delivery fails (non-2xx response or timeout), the system retries delivery up to 3 times with increasing delays between attempts. After all retries are exhausted, the webhook delivery is marked as permanently failed. Each retry attempt is recorded in the delivery history for debugging.

## Acceptance Criteria

1. A failed webhook delivery (non-2xx status code or timeout) is retried up to 3 additional times.
2. Retry delays follow exponential backoff: 10 seconds, 60 seconds, 300 seconds (5 minutes).
3. Each retry attempt is recorded as a separate entry in the webhook_deliveries table with an incremented retry_count.
4. The retry payload and signature are identical to the original delivery attempt.
5. If a retry succeeds (2xx response), no further retries are attempted.
6. After all 3 retries fail, the delivery is marked as permanently failed with no further attempts.
7. Retries are processed asynchronously and do not block any API request.
8. The webhook delivery history shows all attempts (original plus retries) for a given event.
9. When a project is deleted and cascading webhooks fire, the retry mechanism handles those deliveries consistently.
10. If a webhook is deactivated or deleted between retries, remaining retries for that webhook are cancelled.

## API Endpoints

Not applicable. This requirement covers internal retry behavior for webhook deliveries. Delivery status is visible via the webhook delivery history endpoint defined in REQ-WEBHOOK-004.

### Delivery record with retry information

```json
{
  "id": 15,
  "webhook_id": 1,
  "event_type": "resource.created",
  "payload": {"event_type": "resource.created", "data": {"id": 10}},
  "status_code": 500,
  "response_body": "Internal Server Error",
  "delivered_at": "2026-01-15T10:30:10Z",
  "retry_count": 1
}
```

## Dependencies

- REQ-WEBHOOK-002: Requires webhook event delivery to generate the initial delivery attempts that may need retrying.
- REQ-PROJ-003: Requires project deletion with resource cascade to trigger webhook events during cascading deletes.
