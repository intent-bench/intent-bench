# REQ-PROD-002: Product Categories

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement CRUD operations for product categories with hierarchical nesting support. Categories have a self-referencing parent_id to form a tree structure. Only admin users may create or update categories. All authenticated users can list categories. Each category has a unique slug for URL-friendly identification.

## Acceptance Criteria

1. GET /categories returns the full category tree with nested children.
2. POST /categories creates a new category (admin only) and returns 201 Created.
3. POST /categories with a duplicate slug returns 409 Conflict.
4. PUT /categories/:id updates the category name, slug, or parent_id (admin only).
5. PUT /categories/:id with a duplicate slug returns 409 Conflict.
6. Categories with a null parent_id are root-level categories.
7. Categories with a valid parent_id are nested under their parent in the tree response.
8. Non-admin users receive 403 Forbidden when attempting to create or update categories.
9. GET /categories/:id returns a single category with its children.
10. GET /categories/:id returns 404 Not Found for nonexistent categories.

## API Endpoints

### GET /categories

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "parent_id": null,
      "children": [
        {
          "id": 3,
          "name": "Headphones",
          "slug": "headphones",
          "parent_id": 1,
          "children": []
        }
      ]
    },
    {
      "id": 2,
      "name": "Books",
      "slug": "books",
      "parent_id": null,
      "children": []
    }
  ]
}
```

### POST /categories

**Request:**
```json
{
  "name": "Headphones",
  "slug": "headphones",
  "parent_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Headphones",
  "slug": "headphones",
  "parent_id": 1,
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "slug already exists"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### PUT /categories/:id

**Request:**
```json
{
  "name": "Audio Headphones",
  "slug": "audio-headphones"
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Audio Headphones",
  "slug": "audio-headphones",
  "parent_id": 1,
  "created_at": "2026-01-15T10:30:00Z"
}
```

### GET /categories/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "parent_id": null,
  "children": [
    {
      "id": 3,
      "name": "Headphones",
      "slug": "headphones",
      "parent_id": 1,
      "children": []
    }
  ],
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "category not found"
}
```

## Dependencies

- REQ-PROD-001: Requires the products and categories tables and admin authorization logic.
