# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-CFG-001: Config file created with defaults on first run at XDG location

**Phase:** 1

*Foundation: configuration*

### Acceptance Criteria

1. If `~/.config/bm/config.yaml` (or the XDG override path) does not exist, running any command creates it with default values before proceeding.
2. The default config contains at minimum: `format: table`, `color: true`, and `data_file` pointing to the default data store path.
3. If `XDG_CONFIG_HOME` is set, the config file is created under that directory rather than `~/.config`.
4. The config file is valid YAML and can be opened and edited by hand.
5. If the config directory does not exist, it is created with appropriate permissions (0700 or 0755).

---

## 2. REQ-ERR-001: Exit code 0 on success 1 on error 2 on invalid usage

**Phase:** 1

*CLI contract*

### Acceptance Criteria

1. Every command exits with code 0 when it completes successfully.
2. Every command exits with code 1 when it encounters a runtime error (item not found, I/O failure, data corruption).
3. Every command exits with code 2 when the invocation is invalid (missing required argument, unrecognized flag, wrong number of arguments).
4. Error details are written to stderr; normal output is written to stdout so callers can redirect them independently.
5. `--help` on any command or subcommand exits with code 0.

---

## 3. REQ-CLI-001: Add command accepts URL or text with auto-detection and optional flags

**Phase:** 1

*Core: data ingestion*

### Acceptance Criteria

1. `add <url>` where the argument starts with `http://` or `https://` stores the item as type `bookmark`.
2. `add <text>` where the argument is not a URL stores the item as type `snippet`.
3. `--title`, `--tags`, and `--description` flags are accepted and stored with the item.
4. Tags are comma-separated, normalized to lowercase, and deduplicated before storage.
5. Each stored item receives a stable, unique ID (incrementing integer or UUID) that does not change on subsequent runs.

---

## 4. REQ-CLI-003: Show command displays full details of a single item by ID

**Phase:** 2

**Depends on:** REQ-CLI-001

*Core: single item view*

### Acceptance Criteria

1. `show <id>` for a known ID displays all fields: id, type, title, url or content, tags, description, and creation timestamp.
2. `show <id>` for an unknown ID prints an error message to stderr and exits with code 1.
3. Output is human-readable and clearly labels each field.
4. The command accepts the same `--format` flag as `list` for machine-readable output.
5. Tags are displayed as a comma-separated list in the same normalized form they were stored.

---

## 5. REQ-CLI-004: Edit command updates title tags or description by ID

**Phase:** 2

**Depends on:** REQ-CLI-001

*Core: mutation*

### Acceptance Criteria

1. `edit <id> --title "New title"` updates only the title and leaves all other fields unchanged.
2. `edit <id> --tags "go,cli"` replaces the item's tags with the normalized, deduplicated set.
3. `edit <id> --description "New desc"` updates only the description.
4. Multiple flags may be combined in a single invocation to update several fields at once.
5. `edit <id>` with no flags prints a usage error to stderr and exits with code 2.
6. `edit <id>` for an unknown ID prints an error message to stderr and exits with code 1.

---

## 6. REQ-CLI-005: Delete command removes item and requires --confirm flag

**Phase:** 2

**Depends on:** REQ-CLI-001

*Core: deletion with safety*

### Acceptance Criteria

1. `delete <id> --confirm` removes the item and exits with code 0.
2. `delete <id>` without `--confirm` in a non-interactive context prints an error and exits with code 1 without modifying the store.
3. `delete <id>` for an unknown ID prints an error to stderr and exits with code 1.
4. After successful deletion the item no longer appears in `list` or `show` output.
5. The deleted item's ID is not reused for subsequently added items.

---

## 7. REQ-TAG-001: Tag list command shows all tags with item counts

**Phase:** 2

**Depends on:** REQ-CLI-001

*Organization feature*

### Acceptance Criteria

1. `tag list` outputs one row per distinct tag showing the tag name and the number of items that carry it.
2. Tags are displayed in their normalized (lowercase) form.
3. Tags with zero items (orphaned by deletion or rename) do not appear in the output.
4. Output is sorted alphabetically by tag name by default.
5. `tag list` with no tags in the library prints an empty result and exits with code 0.

---

## 8. REQ-CFG-002: Config set and show commands manage configuration values

**Phase:** 2

**Depends on:** REQ-CFG-001

*User preferences*

### Acceptance Criteria

1. `config show` prints all current configuration keys and their values in a human-readable format.
2. `config set format json` updates the `format` key and persists the change to the config file.
3. `config set color false` updates the `color` key; subsequent commands respect the new value.
4. `config set <unknown-key> <value>` prints an error to stderr and exits with code 1 without modifying the config file.
5. `config set` with missing key or value arguments prints a usage error and exits with code 2.

---

## 9. REQ-CLI-002: List command shows items with filtering by type and tag

**Phase:** 2

**Depends on:** REQ-CLI-001

*Core: data retrieval*

### Acceptance Criteria

1. `list` with no flags displays all items in table format with aligned columns and headers.
2. `--type bookmark` or `--type snippet` restricts output to items of that type.
3. `--tag <tag>` restricts output to items that carry the specified tag.
4. `--format json` produces valid JSON; `--format csv` produces valid CSV with a header row.
5. `--type` and `--tag` may be combined to filter by both type and tag simultaneously.

---

## 10. REQ-FMT-001: List and export support table json and csv output formats

**Phase:** 2

**Depends on:** REQ-CLI-002

*Cross-cutting: all list commands*

### Acceptance Criteria

1. Table format renders column headers and rows with consistent alignment; columns are separated by at least one space and headers are visually distinct.
2. JSON format produces a valid JSON array where each element is an object with all item fields; the output passes a JSON schema validator.
3. CSV format produces a header row followed by one data row per item; all fields are correctly quoted when they contain commas, newlines, or quote characters.
4. `--format` is case-insensitive; `--format JSON` and `--format json` are equivalent.
5. An unrecognized format value prints an error to stderr and exits with code 2.

---

## 11. REQ-CLI-006: Search command performs case-insensitive partial match across title description and content

**Phase:** 3

**Depends on:** REQ-CLI-001

*Requires indexed content*

### Acceptance Criteria

1. `search <query>` returns all items where the query string appears (case-insensitively) in the title, description, or content field.
2. Matches are partial: searching for "py" matches items containing "python" or "py script".
3. Results are displayed in the same table format as `list` by default; `--format json|csv` overrides the format.
4. `search <query>` with no matching items prints an empty result (not an error) and exits with code 0.
5. `search` with no query argument prints a usage error and exits with code 2.

---

## 12. REQ-IO-001: Export command writes all items in json or csv format

**Phase:** 3

**Depends on:** REQ-FMT-001

*Data portability*

### Acceptance Criteria

1. `export --format json` writes a valid JSON array of all items to stdout.
2. `export --format csv` writes a valid CSV file with a header row and one row per item to stdout.
3. `export --format <fmt> --output <file>` writes output to the specified file path instead of stdout.
4. An export of an empty library produces a valid empty structure (empty JSON array `[]` or CSV header row only), not an error.
5. `export` with an unrecognized format value prints an error to stderr and exits with code 2.

---

## 13. REQ-IO-002: Import command reads items from json or csv file

**Phase:** 3

**Depends on:** REQ-IO-001

*Data portability*

### Acceptance Criteria

1. `import <file.json>` reads a JSON array of item objects and adds each as a new item with a freshly assigned ID.
2. `import <file.csv>` reads a CSV file with a header row and adds each data row as a new item.
3. Items imported from a valid export file (produced by REQ-IO-001) round-trip correctly: all fields are preserved.
4. `import <file>` where the file does not exist prints an error to stderr and exits with code 1.
5. `import <file>` where the file is malformed (invalid JSON or CSV) prints a descriptive error to stderr and exits with code 1 without adding partial data.

---

## 14. REQ-TAG-002: Tag rename command updates tag across all items

**Phase:** 3

**Depends on:** REQ-TAG-001

*Bulk mutation*

### Acceptance Criteria

1. `tag rename <old> <new>` replaces the old tag with the new tag on every item that carries it.
2. The new tag name is normalized to lowercase and deduplicated against existing tags on each item.
3. If an item already carries both the old and the new tag, the rename results in a single normalized tag (no duplicates).
4. `tag rename <old> <new>` where `<old>` does not exist prints an error to stderr and exits with code 1.
5. After a successful rename `tag list` no longer shows the old tag.

---
