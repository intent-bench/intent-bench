# REQ-CART-002: Cart Validation

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Implement inventory-aware validation for shopping cart operations. Cart item quantities must not exceed the available inventory (quantity minus reserved_quantity). When adding or updating cart items, the system must check current stock levels. If a product goes out of stock after being added to the cart, the item is flagged but not automatically removed. Subtotal calculations use the current unit price of each product.

## Acceptance Criteria

1. POST /cart rejects adding a quantity that exceeds the available inventory (quantity - reserved_quantity) with 400 Bad Request.
2. PUT /cart/:item_id rejects updating to a quantity that exceeds the available inventory with 400 Bad Request.
3. The error response for insufficient stock includes the available quantity.
4. If a product's available inventory drops to zero after being added to a cart, the item remains in the cart but is flagged with an out_of_stock indicator.
5. GET /cart includes an out_of_stock boolean on each cart item reflecting current inventory availability.
6. Cart subtotal for each item is calculated as item quantity multiplied by the product's current unit price.
7. The cart_total reflects the sum of all item subtotals using current prices.
8. Updating a cart item quantity to a value within available stock succeeds with 200 OK.
9. Adding zero or negative quantity returns 400 Bad Request.

## API Endpoints

### POST /cart (insufficient stock)

**Request:**
```json
{
  "product_id": 1,
  "quantity": 999
}
```

**Error (400 Bad Request):**
```json
{
  "error": "insufficient stock",
  "available": 45
}
```

### GET /cart (with out-of-stock item)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "price": 79.99,
      "image_url": "https://example.com/images/wh-1000.jpg",
      "quantity": 2,
      "subtotal": 159.98,
      "out_of_stock": false
    },
    {
      "id": 2,
      "product_id": 5,
      "name": "Vintage Record Player",
      "price": 249.99,
      "image_url": "https://example.com/images/vrp-100.jpg",
      "quantity": 1,
      "subtotal": 249.99,
      "out_of_stock": true
    }
  ],
  "cart_total": 409.97
}
```

### PUT /cart/:item_id (insufficient stock)

**Request:**
```json
{
  "quantity": 500
}
```

**Error (400 Bad Request):**
```json
{
  "error": "insufficient stock",
  "available": 45
}
```

## Dependencies

- REQ-CART-001: Requires the shopping cart endpoints to exist for adding and updating items.
