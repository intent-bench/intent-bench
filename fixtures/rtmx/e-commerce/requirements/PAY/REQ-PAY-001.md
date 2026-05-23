# REQ-PAY-001: Payment Processing

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement a payment processing endpoint that accepts payment for a pending order using a mock payment processor. The mock processor succeeds for any amount up to 10000 and rejects amounts exceeding that threshold. A successful payment creates a payment record with method, amount, and a generated transaction ID, and transitions the order status to "paid". Only the order owner may pay for their order, and only orders in "pending" status can be paid.

## Acceptance Criteria

1. POST /orders/:id/pay processes payment for the specified order.
2. The mock payment processor accepts any amount where amount <= 10000.
3. The mock payment processor rejects amounts where amount > 10000 with a payment failure error.
4. A successful payment creates a payment record with method, amount, and a UUID transaction_id.
5. A successful payment transitions the order status from "pending" to "paid".
6. POST /orders/:id/pay returns 400 if the order is not in "pending" status.
7. POST /orders/:id/pay returns 403 if the authenticated user is not the order owner.
8. POST /orders/:id/pay returns 404 if the order does not exist.
9. The payment record stores the payment method (e.g., "credit_card", "debit_card").
10. POST /orders/:id/pay returns 402 Payment Required when the mock processor rejects the payment.

## API Endpoints

### POST /orders/:id/pay

**Request:**
```json
{
  "method": "credit_card"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 5,
  "method": "credit_card",
  "amount": 79.98,
  "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "created_at": "2026-01-20T14:05:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "order is not in pending status"
}
```

**Error (402 Payment Required):**
```json
{
  "error": "payment rejected: amount exceeds processor limit"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "not authorized to pay for this order"
}
```

## Dependencies

- REQ-ORD-001: Requires order placement to create orders that can be paid.
