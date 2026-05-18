# REQ-RSS-002: Feed Auto-Discovery

## Requirement
Add feed link tag to HTML output for auto-discovery.

## Acceptance Criteria
- All generated HTML pages include `<link rel="alternate" type="application/atom+xml" href="/feed.xml">` in the `<head>`
- Link is present in both index and post pages

## Dependencies
- REQ-RSS-001 (feed must exist before linking to it)

## Test
`TestFeedDiscovery` in `zs_test.go`
