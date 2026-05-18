"""Test suite for the bookmark/snippet manager CLI.

The implementation must provide a CLI tool accessible as a Python module
or script. Tests invoke it via subprocess. The entry point should be
discoverable as `python -m bm`, `python main.py`, or `python app.py`.
"""

import json
import os
import subprocess
import tempfile

import pytest


def find_entry_point():
    """Find the CLI entry point."""
    for candidate in ["main.py", "app.py", "cli.py", "bm.py"]:
        if os.path.exists(candidate):
            return ["python3", candidate]
    # Try as module
    return ["python3", "-m", "bm"]


ENTRY = find_entry_point()


@pytest.fixture
def tmp_config(tmp_path):
    """Set up isolated config and data directories."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = str(config_dir)
    env["BM_DATA_DIR"] = str(data_dir)
    env["HOME"] = str(tmp_path)
    return env


def run_cmd(args, env=None, input_text=None):
    """Run the CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ENTRY + args,
        capture_output=True,
        text=True,
        env=env,
        input=input_text,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


class TestAdd:
    def test_add_bookmark(self, tmp_config):
        code, out, _ = run_cmd(["add", "https://example.com", "--title", "Example"], env=tmp_config)
        assert code == 0

    def test_add_snippet(self, tmp_config):
        code, out, _ = run_cmd(["add", "print('hello world')", "--title", "Hello"], env=tmp_config)
        assert code == 0

    def test_add_with_tags(self, tmp_config):
        code, out, _ = run_cmd(
            ["add", "https://go.dev", "--title", "Go", "--tags", "lang,programming"],
            env=tmp_config,
        )
        assert code == 0

    def test_auto_detect_url(self, tmp_config):
        run_cmd(["add", "https://rust-lang.org", "--title", "Rust"], env=tmp_config)
        code, out, _ = run_cmd(["list", "--type", "bookmark", "--format", "json"], env=tmp_config)
        assert code == 0
        items = json.loads(out)
        assert any("rust-lang" in item.get("url", item.get("content", "")).lower() for item in items)

    def test_auto_detect_snippet(self, tmp_config):
        run_cmd(["add", "SELECT * FROM users", "--title", "SQL"], env=tmp_config)
        code, out, _ = run_cmd(["list", "--type", "snippet", "--format", "json"], env=tmp_config)
        assert code == 0
        items = json.loads(out)
        assert len(items) >= 1


class TestList:
    def test_list_empty(self, tmp_config):
        code, out, _ = run_cmd(["list"], env=tmp_config)
        assert code == 0

    def test_list_table_format(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "Ex"], env=tmp_config)
        code, out, _ = run_cmd(["list"], env=tmp_config)
        assert code == 0
        assert "Ex" in out

    def test_list_json_format(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "JSON Test"], env=tmp_config)
        code, out, _ = run_cmd(["list", "--format", "json"], env=tmp_config)
        assert code == 0
        data = json.loads(out)
        assert isinstance(data, list)

    def test_list_csv_format(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "CSV Test"], env=tmp_config)
        code, out, _ = run_cmd(["list", "--format", "csv"], env=tmp_config)
        assert code == 0
        lines = out.strip().split("\n")
        assert len(lines) >= 2  # header + data

    def test_filter_by_tag(self, tmp_config):
        run_cmd(["add", "https://a.com", "--title", "A", "--tags", "alpha"], env=tmp_config)
        run_cmd(["add", "https://b.com", "--title", "B", "--tags", "beta"], env=tmp_config)
        code, out, _ = run_cmd(["list", "--tag", "alpha", "--format", "json"], env=tmp_config)
        assert code == 0
        items = json.loads(out)
        assert all("alpha" in item.get("tags", []) for item in items)


class TestShowEditDelete:
    def _add_item(self, env):
        run_cmd(["add", "https://example.com", "--title", "Item"], env=env)
        _, out, _ = run_cmd(["list", "--format", "json"], env=env)
        items = json.loads(out)
        return items[0]["id"]

    def test_show(self, tmp_config):
        item_id = self._add_item(tmp_config)
        code, out, _ = run_cmd(["show", str(item_id)], env=tmp_config)
        assert code == 0
        assert "Item" in out

    def test_edit(self, tmp_config):
        item_id = self._add_item(tmp_config)
        code, _, _ = run_cmd(["edit", str(item_id), "--title", "Updated"], env=tmp_config)
        assert code == 0
        _, out, _ = run_cmd(["show", str(item_id)], env=tmp_config)
        assert "Updated" in out

    def test_delete_with_confirm(self, tmp_config):
        item_id = self._add_item(tmp_config)
        code, _, _ = run_cmd(["delete", str(item_id), "--confirm"], env=tmp_config)
        assert code == 0

    def test_delete_without_confirm(self, tmp_config):
        item_id = self._add_item(tmp_config)
        code, _, _ = run_cmd(["delete", str(item_id)], env=tmp_config)
        assert code != 0  # Should fail without --confirm


class TestSearch:
    def test_search_by_title(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "Unique Searchable Title"], env=tmp_config)
        code, out, _ = run_cmd(["search", "Unique Searchable"], env=tmp_config)
        assert code == 0
        assert "Unique" in out

    def test_search_case_insensitive(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "CamelCase"], env=tmp_config)
        code, out, _ = run_cmd(["search", "camelcase"], env=tmp_config)
        assert code == 0
        assert "CamelCase" in out


class TestTags:
    def test_tag_list(self, tmp_config):
        run_cmd(["add", "https://a.com", "--title", "A", "--tags", "go,rust"], env=tmp_config)
        run_cmd(["add", "https://b.com", "--title", "B", "--tags", "go,python"], env=tmp_config)
        code, out, _ = run_cmd(["tag", "list"], env=tmp_config)
        assert code == 0
        assert "go" in out

    def test_tag_rename(self, tmp_config):
        run_cmd(["add", "https://a.com", "--title", "A", "--tags", "oldname"], env=tmp_config)
        code, _, _ = run_cmd(["tag", "rename", "oldname", "newname"], env=tmp_config)
        assert code == 0
        _, out, _ = run_cmd(["list", "--tag", "newname", "--format", "json"], env=tmp_config)
        items = json.loads(out)
        assert len(items) >= 1

    def test_tags_normalized_lowercase(self, tmp_config):
        run_cmd(["add", "https://a.com", "--title", "A", "--tags", "GoLang,RUST"], env=tmp_config)
        _, out, _ = run_cmd(["list", "--format", "json"], env=tmp_config)
        items = json.loads(out)
        tags = items[0].get("tags", [])
        assert all(t == t.lower() for t in tags)


class TestExportImport:
    def test_export_json(self, tmp_config):
        run_cmd(["add", "https://example.com", "--title", "Export"], env=tmp_config)
        code, out, _ = run_cmd(["export", "--format", "json"], env=tmp_config)
        assert code == 0
        data = json.loads(out)
        assert len(data) >= 1

    def test_import_json(self, tmp_config):
        run_cmd(["add", "https://original.com", "--title", "Original"], env=tmp_config)
        _, export_out, _ = run_cmd(["export", "--format", "json"], env=tmp_config)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir=tmp_config.get("HOME", "/tmp")
        ) as f:
            f.write(export_out)
            f.flush()
            code, _, _ = run_cmd(["import", f.name], env=tmp_config)
        assert code == 0


class TestConfig:
    def test_config_show(self, tmp_config):
        code, out, _ = run_cmd(["config", "show"], env=tmp_config)
        assert code == 0

    def test_config_set(self, tmp_config):
        code, _, _ = run_cmd(["config", "set", "default_format", "json"], env=tmp_config)
        assert code == 0


class TestExitCodes:
    def test_invalid_command(self, tmp_config):
        code, _, _ = run_cmd(["nonexistent"], env=tmp_config)
        assert code == 2

    def test_help(self, tmp_config):
        code, out, _ = run_cmd(["--help"], env=tmp_config)
        assert code == 0
        assert "usage" in out.lower() or "help" in out.lower() or "commands" in out.lower()
