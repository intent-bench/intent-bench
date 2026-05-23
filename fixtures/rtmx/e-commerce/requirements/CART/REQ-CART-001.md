# REQ-CART-001: Shopping Cart

## Status: MISSING
## Priority: P0
## Phase: 3

## Requirement

Implement shopping cart functionality allowing authenticated users to add, update, view, and remove items from their cart. Each user has one active cart. The cart displays product details and a subtotal for each item. Users cannot add inactive products to the cart. Clearing the cart removes all items at once.

## Acceptance Criteria

1. GET /cart returns the authenticated user's cart items with product details (name, price, image_url) and per-item subtotal.
2. GET /cart includes a cart_total representing the sum of all item subtotals.
3. POST /cart adds an item to the cart with product_id and quantity, returning 201 Created.
4. POST /cart with a product_id for an inactive product returns 400 Bad Request.
5. POST /cart for a product already in the cart increments the existing quantity rather than creating a duplicate entry.
6. PUT /cart/:item_id updates the quantity of a cart item and returns 200 OK.
7. PUT /cart/:item_id with quantity of 0 removes the item from the cart.
8. DELETE /cart/:item_id removes a specific item from the cart and returns 200 OK.
9. DELETE /cart clears all items from the authenticated user's cart and returns 200 OK.
10. GET /cart returns 401 Unauthorized when no valid token is provided.
11. PUT /cart/:item_id returns 404 Not Found for items not belonging to the authenticated user.

## API Endpoints

### GET /cart

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
      "subtotal": 159.98
    }
  ],
  "cart_total": 159.98
}
```

### POST /cart

**Request:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product_id": 1,
  "name": "Wireless Headphones",
  "price": 79.99,
  "quantity": 2,
  "subtotal": 159.98
}
```

**Error (400 Bad Request):**
```json
{
  "error": "product is not available"
}
```

### PUT /cart/:item_id

**Request:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product_id": 1,
  "name": "Wireless Headphones",
  "price": 79.99,
  "quantity": 3,
  "subtotal": 239.97
}
```

**Error (404 Not Found):**
```json
{
  "error": "cart item not found"
}
```

### DELETE /cart/:item_id

**Response (200 OK):**
```json
{
  "message": "item removed from cart"
}
```

### DELETE /cart

**Response (200 OK):**
```json
{
  "message": "cart cleared"
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication to identify the cart owner.
- REQ-PROD-001: Requires the products table to validate product existence and active status.
- REQ-INV-001: Requires inventory records to exist for stock-aware cart operations.
