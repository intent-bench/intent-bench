# REQ-RSS-001: Atom Feed Generation

## Requirement
Generate valid Atom feed at `/feed.xml` with 20 most recent posts.

## Acceptance Criteria
- Output includes a valid Atom XML file at `/feed.xml`
- Feed contains up to 20 entries sorted by date descending
- Each entry includes: title, date, URL, summary (first 150 chars of content)
- Feed validates against Atom specification

## Dependencies
- REQ-VALID-001, REQ-VALID-002 (front matter must be parsed correctly to extract dates)

## Test
`TestAtomFeed` in `zs_test.go`
