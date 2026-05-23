# REQ-NOTIF-002: Order Notifications

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement automated notification creation at key order lifecycle events. The system automatically creates a notification for the order owner when an order is placed, when payment is received, when a shipment is created, and when a shipment is delivered. Each notification includes the order ID and relevant contextual details in the body.

## Acceptance Criteria

1. An "order_placed" notification is created for the user when POST /orders succeeds.
2. A "payment_received" notification is created for the user when POST /orders/:id/pay succeeds.
3. An "order_shipped" notification is created for the user when POST /orders/:id/ship succeeds.
4. An "order_delivered" notification is created for the user when a shipment status is updated to "delivered".
5. Each notification includes the order ID in the body text.
6. The "order_placed" notification body includes the order total.
7. The "payment_received" notification body includes the payment amount and transaction ID.
8. The "order_shipped" notification body includes the carrier and tracking number.
9. The "order_delivered" notification body includes the delivery timestamp.
10. All auto-created notifications have is_read set to false.
11. Notifications are created for the order owner, not the admin performing the action.

## API Endpoints

### Automatic notification creation (no dedicated endpoint)

Notifications are created as side effects of existing endpoints. The following examples show the notification records produced.

**order_placed notification:**
```json
{
  "id": 1,
  "user_id": 1,
  "type": "order_placed",
  "subject": "Order Confirmed",
  "body": "Your order #5 has been placed. Total: $79.98.",
  "is_read": false,
  "created_at": "2026-01-20T14:00:00Z"
}
```

**payment_received notification:**
```json
{
  "id": 2,
  "user_id": 1,
  "type": "payment_received",
  "subject": "Payment Received",
  "body": "Payment of $79.98 received for order #5. Transaction: a1b2c3d4-e5f6-7890-abcd-ef1234567890.",
  "is_read": false,
  "created_at": "2026-01-20T14:05:00Z"
}
```

**order_shipped notification:**
```json
{
  "id": 3,
  "user_id": 1,
  "type": "order_shipped",
  "subject": "Order Shipped",
  "body": "Your order #5 has been shipped via FedEx. Tracking: FX-1234567890.",
  "is_read": false,
  "created_at": "2026-01-22T08:00:00Z"
}
```

**order_delivered notification:**
```json
{
  "id": 4,
  "user_id": 1,
  "type": "order_delivered",
  "subject": "Order Delivered",
  "body": "Your order #5 was delivered on 2026-01-25T15:30:00Z.",
  "is_read": false,
  "created_at": "2026-01-25T15:30:00Z"
}
```

## Dependencies

- REQ-NOTIF-001: Requires notification system infrastructure for creating and storing notifications.
- REQ-ORD-002: Requires order status tracking for order lifecycle events.
- REQ-SHIP-002: Requires shipment status tracking for shipped and delivered events.
