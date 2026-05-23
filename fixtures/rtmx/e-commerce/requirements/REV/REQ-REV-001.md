# REQ-REV-001: Review Submission

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement a product review submission endpoint that allows authenticated users to post reviews for products they have purchased and received. A user must have at least one delivered order containing the product before they can review it. Each review requires a rating (1-5), title, and body. Users may submit only one review per product. New reviews default to unapproved status and must be moderated before appearing in public listings.

## Acceptance Criteria

1. POST /products/:id/reviews creates a new review for the specified product.
2. The user must have at least one delivered order containing the product to submit a review.
3. POST /products/:id/reviews returns 403 if the user has no delivered order containing the product.
4. Rating must be an integer between 1 and 5 inclusive.
5. Title and body fields are required and must be non-empty.
6. POST /products/:id/reviews returns 422 if rating, title, or body is missing or invalid.
7. A user may submit only one review per product.
8. POST /products/:id/reviews returns 409 if the user has already reviewed the product.
9. Newly created reviews have is_approved set to false by default.
10. GET /products/:id/reviews returns a paginated list of approved reviews only.
11. GET /products/:id/reviews supports page and per_page query parameters.
12. Unapproved reviews are not visible in the GET /products/:id/reviews listing.

## API Endpoints

### POST /products/:id/reviews

**Request:**
```json
{
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product_id": 3,
  "user_id": 1,
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended.",
  "is_approved": false,
  "created_at": "2026-01-26T10:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "you must have a delivered order containing this product to submit a review"
}
```

**Error (409 Conflict):**
```json
{
  "error": "you have already reviewed this product"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "rating must be between 1 and 5"
}
```

### GET /products/:id/reviews

**Request:**
```
GET /products/3/reviews?page=1&per_page=10
```

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": 1,
      "product_id": 3,
      "user_id": 1,
      "username": "alice",
      "rating": 5,
      "title": "Excellent product",
      "body": "This widget exceeded my expectations. Highly recommended.",
      "created_at": "2026-01-26T10:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication to identify the reviewing user.
- REQ-PROD-001: Requires products to exist for review submission.
- REQ-ORD-002: Requires order status tracking to verify delivered status.
- REQ-SHIP-002: Requires shipment delivery to establish purchase eligibility.
