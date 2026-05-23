# REQ-ANALYTICS-003: Analytics Data Export

## Status: MISSING
## Priority: MEDIUM
## Phase: 9

## Requirement

Implement an analytics data export endpoint that allows platform administrators to download analytics data in CSV format for external analysis and reporting. The export supports filtering by date range and metric type, enabling integration with external business intelligence tools and spreadsheet applications.

## Acceptance Criteria

1. GET /admin/analytics/export returns analytics data in CSV format.
2. The response Content-Type is text/csv with a Content-Disposition header for file download.
3. The CSV includes columns for org_id, org_name, plan, metric, value, and period.
4. GET /admin/analytics/export supports start_date and end_date query parameters to filter by date range.
5. GET /admin/analytics/export supports a metrics query parameter to filter by specific metric types (api_calls, storage_bytes, resources_created).
6. GET /admin/analytics/export returns 403 if the authenticated user does not have is_platform_admin=true.
7. The CSV export includes a header row with column names.
8. Large exports are streamed to avoid memory exhaustion.
9. The default date range is the current billing period if no date parameters are provided.

## API Endpoints

### GET /admin/analytics/export

**Request:**
```
GET /admin/analytics/export?start_date=2026-01-01&end_date=2026-01-31&metrics=api_calls,resources_created
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="analytics-2026-01.csv"
```

```csv
org_id,org_name,plan,metric,value,period
1,Acme Corp,business,api_calls,12450,2026-01
1,Acme Corp,business,resources_created,87,2026-01
2,Startup Co,starter,api_calls,3200,2026-01
2,Startup Co,starter,resources_created,24,2026-01
```

**Error (403 Forbidden):**
```json
{
  "error": "platform admin access required"
}
```

## Dependencies

- REQ-ANALYTICS-002: Requires platform-wide analytics to provide the aggregated data for export.
