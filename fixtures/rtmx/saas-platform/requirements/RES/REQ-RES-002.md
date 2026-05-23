# REQ-RES-002: Resource Filtering

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement filtering and listing capabilities for resources within a project. Users can filter resources by type, status, and search term. All list endpoints support pagination with a default page size of 20 and a maximum of 100. Filters are applied as query parameters and can be combined.

## Acceptance Criteria

1. GET /orgs/:slug/projects/:id/resources supports a type query parameter to filter by resource type.
2. GET /orgs/:slug/projects/:id/resources supports a status query parameter to filter by status (active, archived, deleted).
3. GET /orgs/:slug/projects/:id/resources supports a search query parameter that matches against resource name.
4. Multiple filters can be combined (e.g., ?type=database&status=active).
5. Pagination is supported with page and per_page query parameters.
6. The default page size is 20 and the maximum is 100; requesting more than 100 clamps to 100.
7. The response includes pagination metadata (total count, current page, per_page, total pages).
8. Resources with status "deleted" are excluded from listings unless status=deleted is explicitly specified.
9. An invalid status filter value returns 422 Unprocessable Entity.
10. Filtering is case-insensitive for the search parameter.
11. An empty result set returns 200 OK with an empty array, not 404.

## API Endpoints

### GET /orgs/:slug/projects/:id/resources?type=database&status=active&search=prod&page=1&per_page=10

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "name": "Production Database",
      "type": "database",
      "metadata": {
        "engine": "postgresql",
        "version": "15"
      },
      "status": "active",
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  }
}
```

### GET /orgs/:slug/projects/:id/resources (empty result)

**Response (200 OK):**
```json
{
  "data": [],
  "pagination": {
    "total": 0,
    "page": 1,
    "per_page": 20,
    "total_pages": 0
  }
}
```

## Dependencies

- REQ-RES-001: Requires resource CRUD so that resources exist to be filtered.
