# REQ-ORD-002: Order Status

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement order status tracking with a defined state machine governing valid transitions. Order status progresses through: pending, paid, shipped, in_transit, delivered, or cancelled. Only valid transitions are allowed. Cancelling a pending order releases reserved inventory. A status history endpoint provides the complete log of status changes for an order.

## Acceptance Criteria

1. Orders support the following status values: pending, paid, shipped, in_transit, delivered, cancelled.
2. The valid status transitions are: pending to paid, paid to shipped, shipped to in_transit, in_transit to delivered, and pending to cancelled.
3. PUT /orders/:id/status with an invalid transition returns 422 Unprocessable Entity with the current status and allowed transitions.
4. When an order is cancelled (pending to cancelled), all reserved_quantity values for the order's items are decremented (released).
5. GET /orders/:id returns the order with its current status and all order items.
6. GET /orders/:id/history returns the chronological list of status changes with timestamps.
7. Only the order's owner or an admin can view or update the order status.
8. GET /orders/:id returns 404 Not Found for orders not belonging to the authenticated user (unless admin).
9. Each status change is recorded in the audit_log with the old and new status values.
10. PUT /orders/:id/status on an already delivered or cancelled order returns 422 Unprocessable Entity.
11. GET /orders lists all orders for the authenticated user with pagination.

## API Endpoints

### PUT /orders/:id/status

**Request:**
```json
{
  "status": "paid"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "paid",
  "previous_status": "pending",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "invalid status transition",
  "current_status": "pending",
  "allowed_transitions": ["paid", "cancelled"]
}
```

### GET /orders/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "status": "paid",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "quantity": 2,
      "unit_price": 79.99,
      "subtotal": 159.98
    }
  ],
  "total": 127.98,
  "shipping_address": "123 Main St, Springfield, IL 62704",
  "created_at": "2026-01-20T14:00:00Z",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "order not found"
}
```

### GET /orders/:id/history

**Response (200 OK):**
```json
{
  "order_id": 1,
  "history": [
    {
      "from_status": null,
      "to_status": "pending",
      "timestamp": "2026-01-20T14:00:00Z"
    },
    {
      "from_status": "pending",
      "to_status": "paid",
      "timestamp": "2026-01-20T15:00:00Z"
    }
  ]
}
```

### GET /orders

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 1,
      "status": "paid",
      "total": 127.98,
      "created_at": "2026-01-20T14:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

## Dependencies

- REQ-ORD-001: Requires orders to exist before their status can be tracked and transitioned.
