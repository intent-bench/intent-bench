# Task: Build a Bookmark/Snippet Manager CLI

Build a command-line tool for managing a local library of bookmarks and
code snippets. Data is stored in a local file (JSON or SQLite).

## Commands

### Core
- `add <url-or-text>` -- Add a bookmark (URL) or snippet (text). Auto-detect type.
  Accepts `--title`, `--tags`, `--description` flags.
- `list` -- List all items. Supports `--type bookmark|snippet`, `--tag <tag>`,
  `--format table|json|csv` flags. Default format is table.
- `show <id>` -- Show full details of a single item.
- `edit <id>` -- Update an item's title, tags, or description.
  Accepts `--title`, `--tags`, `--description` flags.
- `delete <id>` -- Delete an item. Requires `--confirm` flag or interactive prompt.
- `search <query>` -- Full-text search across titles, descriptions, and content.

### Organization
- `tag list` -- List all tags with item counts.
- `tag rename <old> <new>` -- Rename a tag across all items.
- `export --format json|csv` -- Export all items.
- `import <file>` -- Import items from a JSON or CSV file.

### Configuration
- `config show` -- Show current configuration.
- `config set <key> <value>` -- Set a config value.
- Config file location: `~/.config/bm/config.yaml` (or XDG_CONFIG_HOME).
- Configurable: default output format, data file location, color on/off.

## Requirements

1. Auto-detect whether input is a URL (starts with http/https) or a text snippet
2. Tags are comma-separated, normalized to lowercase, deduplicated
3. Table output is aligned with headers; no external table library required
4. JSON output is valid JSON; CSV output is valid CSV with headers
5. Search is case-insensitive and matches partial strings
6. IDs are stable (not array indices) -- use incrementing integers or UUIDs
7. Delete requires explicit `--confirm` flag in non-interactive mode
8. Config file is created with defaults on first run if it doesn't exist
9. Exit code 0 on success, 1 on error, 2 on invalid usage
10. Include `--help` on all commands with usage examples

## Success Criterion

All tests pass. The tool must work without external services.
