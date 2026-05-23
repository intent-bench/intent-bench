# REQ-DISC-001: Discount Codes

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Implement discount code management and cart application. Admin users can create discount codes with a percentage discount, usage limits, and validity date range. Authenticated users can apply a valid discount code to their cart and remove a previously applied discount. The current_uses counter increments when an order is placed with the discount applied.

## Acceptance Criteria

1. POST /discounts creates a new discount code (admin only) and returns 201 Created.
2. POST /discounts with a duplicate code returns 409 Conflict.
3. The discount_percent must be between 1 and 100 inclusive; values outside this range return 400 Bad Request.
4. POST /cart/apply-discount validates the code exists and is_active before applying.
5. POST /cart/apply-discount validates the code is within the valid_from and valid_until date range.
6. POST /cart/apply-discount validates current_uses is below max_uses (if max_uses is set).
7. POST /cart/apply-discount returns 400 Bad Request with a descriptive error if any validation fails.
8. A successfully applied discount is reflected in the cart_total returned by GET /cart.
9. DELETE /cart/discount removes the applied discount from the cart and returns 200 OK.
10. The current_uses field is incremented when an order is placed with the discount code, not when the code is applied to the cart.
11. Non-admin users receive 403 Forbidden when attempting to create discount codes.

## API Endpoints

### POST /discounts

**Request:**
```json
{
  "code": "SUMMER20",
  "discount_percent": 20,
  "max_uses": 100,
  "valid_from": "2026-06-01T00:00:00Z",
  "valid_until": "2026-08-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "code": "SUMMER20",
  "discount_percent": 20,
  "max_uses": 100,
  "current_uses": 0,
  "valid_from": "2026-06-01T00:00:00Z",
  "valid_until": "2026-08-31T23:59:59Z",
  "is_active": true
}
```

**Error (409 Conflict):**
```json
{
  "error": "discount code already exists"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### POST /cart/apply-discount

**Request:**
```json
{
  "code": "SUMMER20"
}
```

**Response (200 OK):**
```json
{
  "message": "discount applied",
  "discount_percent": 20,
  "cart_total": 127.98,
  "discount_amount": 32.00
}
```

**Error (400 Bad Request):**
```json
{
  "error": "discount code has expired"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "discount code usage limit reached"
}
```

### DELETE /cart/discount

**Response (200 OK):**
```json
{
  "message": "discount removed",
  "cart_total": 159.98
}
```

## Dependencies

- REQ-PROD-001: Requires the products table for price calculations.
- REQ-CART-001: Requires the shopping cart to exist for applying discounts.
