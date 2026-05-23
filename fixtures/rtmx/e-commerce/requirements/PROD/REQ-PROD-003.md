# REQ-PROD-003: Product Search

## Status: MISSING
## Priority: HIGH
## Phase: 3

## Requirement

Implement search and filtering capabilities on the product listing endpoint. Users can search by text across product name and description, filter by category, filter by price range, and sort results. Multiple filters can be combined in a single request. Only active products are returned in all search results.

## Acceptance Criteria

1. GET /products?search=keyword performs a case-insensitive text search across product name and description fields.
2. GET /products?category=id filters products by the specified category_id.
3. GET /products?min_price=X&max_price=Y filters products within the given price range (inclusive).
4. GET /products?sort=price_asc sorts products by price ascending.
5. GET /products?sort=price_desc sorts products by price descending.
6. GET /products?sort=newest sorts products by created_at descending.
7. Multiple filters can be combined (e.g., ?search=phone&category=1&min_price=100&max_price=500&sort=price_asc).
8. Only products with is_active=true are returned regardless of filters applied.
9. Search results include pagination metadata (page, per_page, total).
10. An empty search result returns 200 OK with an empty products array and total of 0.

## API Endpoints

### GET /products?search=wireless&category=3&min_price=50&max_price=100&sort=price_asc

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Wireless Headphones",
      "description": "Bluetooth over-ear headphones with noise cancellation",
      "price": 79.99,
      "sku": "WH-1000",
      "image_url": "https://example.com/images/wh-1000.jpg",
      "category_id": 3,
      "is_active": true,
      "average_rating": 4.5,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### GET /products?search=nonexistent

**Response (200 OK):**
```json
{
  "products": [],
  "page": 1,
  "per_page": 20,
  "total": 0
}
```

## Dependencies

- REQ-PROD-001: Requires the product listing endpoint and products table.
- REQ-PROD-002: Requires categories to exist for category-based filtering.
