# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-TEST-001: All existing tests continue to pass after changes

**Phase:** 1

*Must not break existing functionality*

### Acceptance Criteria

- `go test ./...` exits 0
- No existing test functions are removed or modified to pass
- New functionality does not break existing site generation behavior

---

## 2. REQ-VALID-001: Report error for invalid YAML front matter with filename and line number

**Phase:** 1

*Task A: existing parser silently ignores errors*

### Acceptance Criteria

- When a markdown file contains malformed YAML between `---` delimiters, the generator reports a clear error
- Error message includes the filename and approximate line number
- Processing stops for that file but continues for others
- Exit code is non-zero when errors are encountered

---

## 3. REQ-VALID-002: Warn on missing required title field in front matter

**Phase:** 1

**Depends on:** REQ-VALID-001

*Task A: graceful degradation*

### Acceptance Criteria

- When a markdown file has valid YAML front matter but no `title` field, log a warning
- Processing continues (do not abort)
- The warning includes the filename

---

## 4. REQ-RSS-001: Generate valid Atom feed at /feed.xml with 20 most recent posts

**Phase:** 2

**Depends on:** REQ-VALID-001, REQ-VALID-002

*Task B: requires post date parsing*

### Acceptance Criteria

- Output includes a valid Atom XML file at `/feed.xml`
- Feed contains up to 20 entries sorted by date descending
- Each entry includes: title, date, URL, summary (first 150 chars of content)
- Feed validates against Atom specification

---

## 5. REQ-RSS-002: Add feed link tag to HTML output for auto-discovery

**Phase:** 2

**Depends on:** REQ-RSS-001

*Task B: small template change*

### Acceptance Criteria

- All generated HTML pages include `<link rel="alternate" type="application/atom+xml" href="/feed.xml">` in the `<head>`
- Link is present in both index and post pages

---

## 6. REQ-TAG-001: Parse tags from YAML front matter as normalized lowercase list

**Phase:** 3

*Task C: foundation for tag system*

### Acceptance Criteria

- Tags specified as `tags: [Go, Web, Tutorial]` are parsed into `["go", "web", "tutorial"]`
- Whitespace is trimmed
- Empty strings are ignored
- Duplicate tags are deduplicated

---

## 7. REQ-TAG-002: Generate /tags/ index page listing all tags with post counts

**Phase:** 3

**Depends on:** REQ-TAG-001

*Task C: aggregation across all posts*

### Acceptance Criteria

- Output includes an HTML page at `/tags/index.html`
- Page lists all unique tags across all posts
- Each tag shows the number of posts with that tag
- Tags link to their per-tag page

---

## 8. REQ-TAG-003: Generate per-tag pages at /tags/<tag>/ listing tagged posts

**Phase:** 3

**Depends on:** REQ-TAG-001

*Task C: most complex subtask*

### Acceptance Criteria

- For each unique tag, generate an HTML page at `/tags/<tag>/index.html`
- Page lists all posts with that tag, with titles and dates
- Posts are sorted by date descending

---

## 9. REQ-TAG-004: Handle edge cases: empty tags duplicate tags whitespace-only tags

**Phase:** 3

**Depends on:** REQ-TAG-001

*Task C: robustness*

### Acceptance Criteria

- Empty string tags are silently dropped
- Duplicate tags (after normalization) produce only one tag page
- Whitespace-only tags are treated as empty
- No crash or panic on malformed tag data

---
