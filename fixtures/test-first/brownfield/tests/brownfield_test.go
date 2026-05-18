package main

// Brownfield tests for the zserge/zs static site generator additions.
// These tests verify the three features added to the existing codebase:
// Task A: YAML front matter validation
// Task B: RSS/Atom feed generation
// Task C: Tag support
//
// The agent must implement these features in the existing zs codebase.
// Tests import from the main package (or relevant packages) of the project.

import (
	"encoding/xml"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// --- Task A: YAML Front Matter Validation ---

func TestInvalidYAMLFrontMatter(t *testing.T) {
	tmpDir := t.TempDir()
	// Create a markdown file with invalid YAML front matter
	content := `---
title: [invalid yaml
  broken: {
---
# Hello`
	path := filepath.Join(tmpDir, "bad.md")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	// The build should report an error for invalid YAML
	// This tests that the generator no longer silently ignores malformed front matter
	err := buildSite(tmpDir, t.TempDir())
	if err == nil {
		t.Fatal("expected error for invalid YAML front matter, got nil")
	}
	if !strings.Contains(err.Error(), "bad.md") {
		t.Errorf("error should mention the filename, got: %s", err.Error())
	}
}

func TestMissingTitleWarning(t *testing.T) {
	tmpDir := t.TempDir()
	// Create a markdown file with valid YAML but no title
	content := `---
date: 2024-01-01
---
# Hello`
	path := filepath.Join(tmpDir, "notitle.md")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	// Should succeed (warning only) but processing should continue
	outDir := t.TempDir()
	err := buildSite(tmpDir, outDir)
	if err != nil {
		t.Fatalf("missing title should warn, not fail: %v", err)
	}

	// Output should still be generated
	entries, _ := os.ReadDir(outDir)
	if len(entries) == 0 {
		t.Fatal("output directory should contain generated files")
	}
}

func TestValidFrontMatter(t *testing.T) {
	tmpDir := t.TempDir()
	content := `---
title: Valid Post
date: 2024-01-01
---
# Hello World`
	path := filepath.Join(tmpDir, "valid.md")
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	outDir := t.TempDir()
	err := buildSite(tmpDir, outDir)
	if err != nil {
		t.Fatalf("valid front matter should not produce error: %v", err)
	}
}

// --- Task B: RSS Feed Generation ---

// AtomFeed represents a minimal Atom feed for XML parsing
type AtomFeed struct {
	XMLName xml.Name   `xml:"feed"`
	Title   string     `xml:"title"`
	Entries []AtomEntry `xml:"entry"`
}

type AtomEntry struct {
	Title   string `xml:"title"`
	Link    struct {
		Href string `xml:"href,attr"`
	} `xml:"link"`
	Summary string `xml:"summary"`
}

func TestFeedGeneration(t *testing.T) {
	tmpDir := t.TempDir()

	// Create several posts
	for i, post := range []struct{ title, date string }{
		{"First Post", "2024-01-01"},
		{"Second Post", "2024-01-02"},
		{"Third Post", "2024-01-03"},
	} {
		content := "---\ntitle: " + post.title + "\ndate: " + post.date + "\n---\n" +
			"This is the content of " + post.title + " with enough text to generate a summary."
		path := filepath.Join(tmpDir, "post"+string(rune('0'+i))+".md")
		os.WriteFile(path, []byte(content), 0644)
	}

	outDir := t.TempDir()
	err := buildSite(tmpDir, outDir)
	if err != nil {
		t.Fatalf("build failed: %v", err)
	}

	// Check feed.xml exists
	feedPath := filepath.Join(outDir, "feed.xml")
	feedData, err := os.ReadFile(feedPath)
	if err != nil {
		t.Fatalf("feed.xml not generated: %v", err)
	}

	// Parse and validate Atom feed
	var feed AtomFeed
	if err := xml.Unmarshal(feedData, &feed); err != nil {
		t.Fatalf("invalid Atom XML: %v", err)
	}
	if len(feed.Entries) < 3 {
		t.Errorf("expected at least 3 feed entries, got %d", len(feed.Entries))
	}
}

func TestFeedSortedByDate(t *testing.T) {
	tmpDir := t.TempDir()

	// Create posts in non-chronological order
	posts := []struct{ title, date, file string }{
		{"Old Post", "2024-01-01", "old.md"},
		{"New Post", "2024-12-01", "new.md"},
		{"Mid Post", "2024-06-01", "mid.md"},
	}
	for _, p := range posts {
		content := "---\ntitle: " + p.title + "\ndate: " + p.date + "\n---\nContent."
		os.WriteFile(filepath.Join(tmpDir, p.file), []byte(content), 0644)
	}

	outDir := t.TempDir()
	buildSite(tmpDir, outDir)

	feedData, _ := os.ReadFile(filepath.Join(outDir, "feed.xml"))
	var feed AtomFeed
	xml.Unmarshal(feedData, &feed)

	if len(feed.Entries) >= 2 {
		// Most recent should be first
		if feed.Entries[0].Title != "New Post" {
			t.Errorf("feed should be sorted by date descending, first entry is %q", feed.Entries[0].Title)
		}
	}
}

// --- Task C: Tag Support ---

func TestTagParsing(t *testing.T) {
	tmpDir := t.TempDir()
	content := `---
title: Tagged Post
date: 2024-01-01
tags: [go, web, tutorial]
---
Content.`
	os.WriteFile(filepath.Join(tmpDir, "tagged.md"), []byte(content), 0644)

	outDir := t.TempDir()
	err := buildSite(tmpDir, outDir)
	if err != nil {
		t.Fatalf("build with tags failed: %v", err)
	}

	// Check tag index page exists
	tagIndex := filepath.Join(outDir, "tags", "index.html")
	if _, err := os.Stat(tagIndex); os.IsNotExist(err) {
		t.Fatal("/tags/index.html not generated")
	}

	// Check per-tag pages exist
	for _, tag := range []string{"go", "web", "tutorial"} {
		tagPage := filepath.Join(outDir, "tags", tag, "index.html")
		if _, err := os.Stat(tagPage); os.IsNotExist(err) {
			t.Fatalf("/tags/%s/index.html not generated", tag)
		}
	}
}

func TestTagNormalization(t *testing.T) {
	tmpDir := t.TempDir()
	content := `---
title: Mixed Case Tags
date: 2024-01-01
tags: [Go, WEB, Tutorial]
---
Content.`
	os.WriteFile(filepath.Join(tmpDir, "mixed.md"), []byte(content), 0644)

	outDir := t.TempDir()
	buildSite(tmpDir, outDir)

	// Tags should be normalized to lowercase
	for _, tag := range []string{"go", "web", "tutorial"} {
		tagPage := filepath.Join(outDir, "tags", tag, "index.html")
		if _, err := os.Stat(tagPage); os.IsNotExist(err) {
			t.Fatalf("normalized tag page /tags/%s/ not generated", tag)
		}
	}
	// Uppercase versions should not exist
	for _, tag := range []string{"Go", "WEB", "Tutorial"} {
		tagPage := filepath.Join(outDir, "tags", tag, "index.html")
		if _, err := os.Stat(tagPage); !os.IsNotExist(err) {
			t.Fatalf("unnormalized tag page /tags/%s/ should not exist", tag)
		}
	}
}

func TestTagIndexShowsCounts(t *testing.T) {
	tmpDir := t.TempDir()
	for i, p := range []struct{ title, tags string }{
		{"Post A", "[go, web]"},
		{"Post B", "[go, cli]"},
		{"Post C", "[web]"},
	} {
		content := "---\ntitle: " + p.title + "\ndate: 2024-01-0" + string(rune('1'+i)) + "\ntags: " + p.tags + "\n---\nContent."
		os.WriteFile(filepath.Join(tmpDir, "post"+string(rune('a'+i))+".md"), []byte(content), 0644)
	}

	outDir := t.TempDir()
	buildSite(tmpDir, outDir)

	tagIndex, err := os.ReadFile(filepath.Join(outDir, "tags", "index.html"))
	if err != nil {
		t.Fatal("tags index not generated")
	}
	content := string(tagIndex)

	// "go" should appear (2 posts)
	if !strings.Contains(content, "go") {
		t.Error("tag index should list 'go'")
	}
}

// buildSite is the contract point: the implementation must provide this function
// or an equivalent that builds the site from srcDir to outDir.
// If the implementation uses a different function signature, this file
// should be adapted by the agent.
func buildSite(srcDir, outDir string) error {
	// Placeholder: the agent must wire this to the actual zs build function.
	// Example: return zs.Build(srcDir, outDir)
	return nil
}
