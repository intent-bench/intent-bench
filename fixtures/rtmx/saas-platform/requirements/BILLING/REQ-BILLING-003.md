# REQ-BILLING-003: Invoice Generation

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Implement invoice generation and management for organization billing. The system generates monthly invoices that summarize the billing plan, usage metrics, and total charges for each billing period. Invoices progress through a lifecycle of draft, issued, paid, and overdue statuses. Organization owners can list and view invoice details.

## Acceptance Criteria

1. GET /orgs/:slug/billing/invoices returns a paginated list of invoices for the organization, newest first.
2. GET /orgs/:slug/billing/invoices/:id returns the full details of a specific invoice.
3. Each invoice includes id, org_id, period_start, period_end, amount_cents, status, issued_at, and paid_at.
4. Invoice status progresses through: draft, issued, paid, or overdue.
5. The amount_cents is calculated from the organization's plan price for the billing period.
6. GET /orgs/:slug/billing/invoices returns 403 if the authenticated user is not an owner of the organization.
7. GET /orgs/:slug/billing/invoices/:id returns 404 if the invoice does not exist or belongs to another organization.
8. Invoices are scoped to the organization via tenant isolation.
9. Invoices are generated at the end of each billing period (monthly).
10. Free plan organizations receive invoices with amount_cents of 0.

## API Endpoints

### GET /orgs/:slug/billing/invoices

**Request:**
```
GET /orgs/acme/billing/invoices?page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "invoices": [
    {
      "id": 3,
      "org_id": 1,
      "period_start": "2026-01-01T00:00:00Z",
      "period_end": "2026-01-31T23:59:59Z",
      "amount_cents": 9900,
      "status": "paid",
      "issued_at": "2026-02-01T00:00:00Z",
      "paid_at": "2026-02-05T12:00:00Z"
    },
    {
      "id": 2,
      "org_id": 1,
      "period_start": "2025-12-01T00:00:00Z",
      "period_end": "2025-12-31T23:59:59Z",
      "amount_cents": 2900,
      "status": "paid",
      "issued_at": "2026-01-01T00:00:00Z",
      "paid_at": "2026-01-03T09:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
}
```

### GET /orgs/:slug/billing/invoices/:id

**Response (200 OK):**
```json
{
  "id": 3,
  "org_id": 1,
  "period_start": "2026-01-01T00:00:00Z",
  "period_end": "2026-01-31T23:59:59Z",
  "amount_cents": 9900,
  "status": "paid",
  "issued_at": "2026-02-01T00:00:00Z",
  "paid_at": "2026-02-05T12:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "invoice not found"
}
```

## Dependencies

- REQ-BILLING-002: Requires plan upgrade/downgrade to determine the correct plan price for invoice calculation.
- REQ-QUOTA-002: Requires quota tracking to include usage data in invoice context.
