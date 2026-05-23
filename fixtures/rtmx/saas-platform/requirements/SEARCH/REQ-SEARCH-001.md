# REQ-SEARCH-001: Full-Text Search Across Projects and Resources

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement a full-text search endpoint that searches across project names, project descriptions, resource names, and resource metadata within a single organization. The search is scoped to the authenticated user's organization and returns matching results grouped by entity type. Search results respect tenant isolation and only return entities the user has access to.

## Acceptance Criteria

1. GET /orgs/:slug/search?q=term searches project names and descriptions within the organization.
2. GET /orgs/:slug/search?q=term also searches resource names within the organization.
3. Search is case-insensitive and matches partial terms.
4. Results are grouped by entity type (projects, resources) in the response.
5. Each result includes the entity id, name, type, and a snippet of the matching text.
6. GET /orgs/:slug/search supports page and per_page query parameters for pagination.
7. GET /orgs/:slug/search returns 400 if the q parameter is missing or empty.
8. GET /orgs/:slug/search returns 403 if the authenticated user is not a member of the organization.
9. Search results are scoped to the organization via tenant isolation; no cross-tenant results are returned.
10. Archived projects and soft-deleted resources are excluded from search results by default.
11. Search results are ordered by relevance (exact matches first, then partial matches).

## API Endpoints

### GET /orgs/:slug/search

**Request:**
```
GET /orgs/acme/search?q=report&page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "query": "report",
  "results": {
    "projects": [
      {
        "id": 5,
        "name": "Q4 Report",
        "description": "Quarterly financial analysis and reporting",
        "type": "project"
      }
    ],
    "resources": [
      {
        "id": 22,
        "name": "Monthly Report Template",
        "type": "document",
        "project_id": 3
      },
      {
        "id": 45,
        "name": "Annual Report Data",
        "type": "dataset",
        "project_id": 5
      }
    ]
  },
  "total": 3,
  "page": 1,
  "per_page": 20
}
```

**Error (400 Bad Request):**
```json
{
  "error": "search query parameter 'q' is required"
}
```

## Dependencies

- REQ-RES-002: Requires resource filtering and listing to index resources for search.
