# REQ-SHIP-001: Shipment Creation

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement a shipment creation endpoint that allows administrators to create a shipment for a paid order. The endpoint requires a carrier name and tracking number, creates a shipment record with status "processing", transitions the order status to "shipped", and deducts the reserved quantity from inventory to reflect actual stock reduction upon fulfillment.

## Acceptance Criteria

1. POST /orders/:id/ship creates a new shipment record for the specified order.
2. Only users with the admin role may create shipments.
3. POST /orders/:id/ship returns 403 if the authenticated user is not an admin.
4. Only orders in "paid" status can be shipped.
5. POST /orders/:id/ship returns 400 if the order is not in "paid" status.
6. The request must include carrier and tracking_number fields.
7. POST /orders/:id/ship returns 422 if carrier or tracking_number is missing.
8. The shipment record is created with status "processing".
9. A successful shipment creation transitions the order status from "paid" to "shipped".
10. Upon shipment creation, reserved_quantity for each order item is deducted from inventory (actual stock reduction).
11. POST /orders/:id/ship returns 404 if the order does not exist.

## API Endpoints

### POST /orders/:id/ship

**Request:**
```json
{
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_id": 5,
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890",
  "status": "processing",
  "created_at": "2026-01-22T08:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only paid orders can be shipped"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "carrier and tracking_number are required"
}
```

## Dependencies

- REQ-ORD-001: Requires order placement to create orders that can be shipped.
