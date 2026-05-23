# REQ-PAY-002: Payment Refunds

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement a refund endpoint that allows administrators to refund paid orders that have not yet been shipped. A refund creates a new payment record with a negative amount, transitions the order status to "cancelled", and releases all reserved inventory back to available stock. Only administrators can issue refunds, and only orders in "paid" status (not yet shipped) are eligible.

## Acceptance Criteria

1. POST /orders/:id/refund processes a refund for the specified order.
2. Only users with the admin role may issue refunds.
3. POST /orders/:id/refund returns 403 if the authenticated user is not an admin.
4. Only orders in "paid" status can be refunded.
5. POST /orders/:id/refund returns 400 if the order is not in "paid" status.
6. A refund creates a payment record with a negative amount equal to the original payment amount.
7. The refund payment record includes a new transaction_id (UUID) and method "refund".
8. A successful refund transitions the order status from "paid" to "cancelled".
9. A successful refund releases all reserved_quantity for the order's items back to available inventory.
10. POST /orders/:id/refund returns 404 if the order does not exist.

## API Endpoints

### POST /orders/:id/refund

**Request:**
```
POST /orders/5/refund
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "id": 2,
  "order_id": 5,
  "method": "refund",
  "amount": -79.98,
  "transaction_id": "f1e2d3c4-b5a6-7890-abcd-ef0987654321",
  "status": "completed",
  "created_at": "2026-01-21T10:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only paid orders can be refunded"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

## Dependencies

- REQ-PAY-001: Requires payment processing to create paid orders that can be refunded.
- REQ-ORD-002: Requires order status tracking to transition order to cancelled.
