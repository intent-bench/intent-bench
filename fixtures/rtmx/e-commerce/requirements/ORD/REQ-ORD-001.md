# REQ-ORD-001: Order Placement

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement order placement that atomically converts a shopping cart into an order. The operation validates all items are in stock, reserves inventory by incrementing reserved_quantity, calculates the order total (applying any discount), creates the order and order items, and clears the cart. A shipping address is required. If any item is unavailable, the entire operation fails without partial changes.

## Acceptance Criteria

1. POST /orders creates an order from the authenticated user's cart and returns 201 Created.
2. The order total is calculated from all cart item subtotals, with any applied discount code percentage deducted.
3. A shipping_address field is required; omitting it returns 400 Bad Request.
4. Each product's reserved_quantity is incremented by the ordered quantity during order placement.
5. If any cart item quantity exceeds the product's available inventory, the entire order fails with 400 Bad Request.
6. The error response for insufficient stock identifies which product(s) are unavailable.
7. Order items are created with the unit_price locked at the product's current price at time of order.
8. The cart is cleared after successful order placement.
9. If a discount code is applied, its current_uses is incremented by one.
10. The new order's status is set to "pending".
11. The operation is atomic: if any step fails, no inventory is reserved, no order is created, and the cart is unchanged.
12. POST /orders with an empty cart returns 400 Bad Request.

## API Endpoints

### POST /orders

**Request:**
```json
{
  "shipping_address": "123 Main St, Springfield, IL 62704"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
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
  "subtotal": 159.98,
  "discount_percent": 20,
  "discount_amount": 32.00,
  "total": 127.98,
  "shipping_address": "123 Main St, Springfield, IL 62704",
  "created_at": "2026-01-20T14:00:00Z"
}
```

**Error (400 Bad Request - empty cart):**
```json
{
  "error": "cart is empty"
}
```

**Error (400 Bad Request - insufficient stock):**
```json
{
  "error": "insufficient stock",
  "unavailable_items": [
    {
      "product_id": 5,
      "name": "Vintage Record Player",
      "requested": 3,
      "available": 1
    }
  ]
}
```

**Error (400 Bad Request - missing address):**
```json
{
  "error": "shipping_address is required"
}
```

## Dependencies

- REQ-CART-001: Requires the shopping cart to contain items for conversion to an order.
