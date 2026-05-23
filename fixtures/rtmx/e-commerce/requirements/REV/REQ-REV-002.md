# REQ-REV-002: Review Moderation

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement review moderation endpoints that allow administrators to approve reviews and allow either admins or review authors to delete reviews. Product average_rating and review_count are computed from approved reviews only and included in product detail responses.

## Acceptance Criteria

1. PUT /reviews/:id/approve sets is_approved to true on the specified review.
2. Only users with the admin role may approve reviews.
3. PUT /reviews/:id/approve returns 403 if the authenticated user is not an admin.
4. DELETE /reviews/:id deletes the specified review.
5. Only the review author or an admin may delete a review.
6. DELETE /reviews/:id returns 403 if the user is neither the author nor an admin.
7. DELETE /reviews/:id returns 404 if the review does not exist.
8. Product average_rating is computed from approved reviews only.
9. Product review_count reflects only approved reviews.
10. GET /products/:id includes average_rating and review_count fields.
11. When an approved review is deleted, the product's average_rating and review_count are recalculated.

## API Endpoints

### PUT /reviews/:id/approve

**Request:**
```
PUT /reviews/1/approve
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product_id": 3,
  "user_id": 1,
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended.",
  "is_approved": true,
  "created_at": "2026-01-26T10:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### DELETE /reviews/:id

**Response (204 No Content):**
```
(empty body)
```

**Error (403 Forbidden):**
```json
{
  "error": "not authorized to delete this review"
}
```

### GET /products/:id (with review aggregates)

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Widget",
  "description": "A fine widget",
  "price": 39.99,
  "sku": "WDG-001",
  "average_rating": 4.5,
  "review_count": 12,
  "created_at": "2026-01-10T08:00:00Z"
}
```

## Dependencies

- REQ-REV-001: Requires review submission to produce reviews that can be moderated.
