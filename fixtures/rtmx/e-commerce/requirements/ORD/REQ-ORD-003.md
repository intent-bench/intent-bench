# REQ-ORD-003: Order History

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement order history endpoints that allow users to list their orders with pagination, view individual order details with items, and retrieve the status change log for an order. Users may cancel pending orders, which releases reserved inventory and returns stock. Only the order owner may view or cancel their orders.

## Acceptance Criteria

1. GET /orders returns a paginated list of the authenticated user's orders sorted by creation date (newest first).
2. GET /orders supports page and per_page query parameters with sensible defaults (page=1, per_page=20).
3. GET /orders/:id returns the full order record including line items, totals, and current status.
4. GET /orders/:id returns 404 if the order does not exist or belongs to another user.
5. GET /orders/:id/history returns the chronological list of status changes for the order, each with old_status, new_status, changed_at, and changed_by.
6. PUT /orders/:id/cancel transitions a pending order to "cancelled" status.
7. PUT /orders/:id/cancel releases all reserved_quantity for the order's items back to available inventory.
8. PUT /orders/:id/cancel returns 400 if the order is not in "pending" status.
9. PUT /orders/:id/cancel returns 403 if the authenticated user is not the order owner.
10. A cancellation event is recorded in the order's status change history.

## API Endpoints

### GET /orders

**Request:**
```
GET /orders?page=1&per_page=10
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 5,
      "user_id": 1,
      "status": "paid",
      "total": 79.98,
      "item_count": 2,
      "created_at": "2026-01-20T14:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1
}
```

### GET /orders/:id

**Response (200 OK):**
```json
{
  "id": 5,
  "user_id": 1,
  "status": "paid",
  "total": 79.98,
  "items": [
    {
      "product_id": 3,
      "product_name": "Widget",
      "quantity": 2,
      "unit_price": 39.99
    }
  ],
  "created_at": "2026-01-20T14:00:00Z",
  "updated_at": "2026-01-20T14:05:00Z"
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
  "history": [
    {
      "old_status": null,
      "new_status": "pending",
      "changed_at": "2026-01-20T14:00:00Z",
      "changed_by": 1
    },
    {
      "old_status": "pending",
      "new_status": "paid",
      "changed_at": "2026-01-20T14:05:00Z",
      "changed_by": 1
    }
  ]
}
```

### PUT /orders/:id/cancel

**Response (200 OK):**
```json
{
  "id": 5,
  "status": "cancelled",
  "cancelled_at": "2026-01-21T09:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only pending orders can be cancelled"
}
```

## Dependencies

- REQ-ORD-002: Requires order status tracking for history and cancellation transitions.
