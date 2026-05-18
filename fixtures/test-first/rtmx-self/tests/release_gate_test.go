package cmd

// Tests for the release gate subcommand.
// The agent must implement `release gate <version>` as a Cobra subcommand
// that checks all requirements assigned to the given version via the
// sprint column in the CSV database.

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// createTestDB writes a minimal RTM CSV database to a temp directory.
func createTestDB(t *testing.T, content string) string {
	t.Helper()
	dir := t.TempDir()
	rtmxDir := filepath.Join(dir, ".rtmx")
	if err := os.MkdirAll(rtmxDir, 0755); err != nil {
		t.Fatal(err)
	}
	dbPath := filepath.Join(rtmxDir, "database.csv")
	if err := os.WriteFile(dbPath, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}
	// Write minimal config
	configContent := "project:\n  name: test\nrtm:\n  database: .rtmx/database.csv\n  schema: core\n"
	if err := os.WriteFile(filepath.Join(rtmxDir, "config.yaml"), []byte(configContent), 0644); err != nil {
		t.Fatal(err)
	}
	return dir
}

func TestReleaseGateAllComplete(t *testing.T) {
	db := "id,description,status,priority,category,depends_on,sprint\n" +
		"REQ-001,First requirement,COMPLETE,high,core,,v1.0.0\n" +
		"REQ-002,Second requirement,COMPLETE,medium,core,,v1.0.0\n"
	dir := createTestDB(t, db)

	var stdout, stderr bytes.Buffer
	err := executeReleaseGate(dir, "v1.0.0", false, &stdout, &stderr)
	if err != nil {
		t.Fatalf("all COMPLETE should exit 0, got error: %v\nstderr: %s", err, stderr.String())
	}
	output := stdout.String()
	if !strings.Contains(strings.ToLower(output), "pass") && !strings.Contains(strings.ToLower(output), "ready") {
		t.Errorf("expected success message, got: %s", output)
	}
}

func TestReleaseGateIncomplete(t *testing.T) {
	db := "id,description,status,priority,category,depends_on,sprint\n" +
		"REQ-001,Done requirement,COMPLETE,high,core,,v1.0.0\n" +
		"REQ-002,Pending requirement,IN_PROGRESS,medium,core,,v1.0.0\n" +
		"REQ-003,Not started,DRAFT,low,core,,v1.0.0\n"
	dir := createTestDB(t, db)

	var stdout, stderr bytes.Buffer
	err := executeReleaseGate(dir, "v1.0.0", false, &stdout, &stderr)
	if err == nil {
		t.Fatal("incomplete requirements should exit 1")
	}
	output := stdout.String() + stderr.String()
	if !strings.Contains(output, "REQ-002") {
		t.Errorf("output should list incomplete requirement REQ-002, got: %s", output)
	}
	if !strings.Contains(output, "REQ-003") {
		t.Errorf("output should list incomplete requirement REQ-003, got: %s", output)
	}
}

func TestReleaseGateNoRequirements(t *testing.T) {
	db := "id,description,status,priority,category,depends_on,sprint\n" +
		"REQ-001,Other version,COMPLETE,high,core,,v2.0.0\n"
	dir := createTestDB(t, db)

	var stdout, stderr bytes.Buffer
	err := executeReleaseGate(dir, "v1.0.0", false, &stdout, &stderr)
	if err == nil {
		t.Fatal("no requirements assigned should exit 1")
	}
	output := stdout.String() + stderr.String()
	if !strings.Contains(strings.ToLower(output), "no requirements") && !strings.Contains(strings.ToLower(output), "warning") {
		t.Errorf("expected warning about no requirements, got: %s", output)
	}
}

func TestReleaseGateJSONOutput(t *testing.T) {
	db := "id,description,status,priority,category,depends_on,sprint\n" +
		"REQ-001,First,COMPLETE,high,core,,v1.0.0\n" +
		"REQ-002,Second,IN_PROGRESS,medium,core,,v1.0.0\n"
	dir := createTestDB(t, db)

	var stdout, stderr bytes.Buffer
	err := executeReleaseGate(dir, "v1.0.0", true, &stdout, &stderr)
	// Should fail (incomplete) but produce JSON
	if err == nil {
		t.Fatal("should fail with incomplete requirements")
	}

	var result map[string]interface{}
	if jsonErr := json.Unmarshal(stdout.Bytes(), &result); jsonErr != nil {
		t.Fatalf("--json flag should produce valid JSON, got error: %v\noutput: %s", jsonErr, stdout.String())
	}
}

func TestReleaseGateIgnoresOtherVersions(t *testing.T) {
	db := "id,description,status,priority,category,depends_on,sprint\n" +
		"REQ-001,V1 req,COMPLETE,high,core,,v1.0.0\n" +
		"REQ-002,V2 req,DRAFT,high,core,,v2.0.0\n"
	dir := createTestDB(t, db)

	var stdout, stderr bytes.Buffer
	err := executeReleaseGate(dir, "v1.0.0", false, &stdout, &stderr)
	if err != nil {
		t.Fatalf("v2 incomplete should not affect v1 gate: %v", err)
	}
}

// executeReleaseGate is the contract point.
// The agent must implement this function or wire it to the actual command.
// Parameters:
//   - projectDir: path to the project root containing .rtmx/
//   - version: the target version to check (e.g., "v1.0.0")
//   - jsonOutput: whether to output JSON (--json flag)
//   - stdout, stderr: output writers
//
// Returns nil on success (all requirements COMPLETE), error otherwise.
func executeReleaseGate(projectDir, version string, jsonOutput bool, stdout, stderr *bytes.Buffer) error {
	// Placeholder: the agent must wire this to the actual release gate implementation.
	// Example: return runReleaseGateCmd(projectDir, version, jsonOutput, stdout, stderr)
	return nil
}
