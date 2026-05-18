package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestShortenURL(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	body := `{"url": "https://example.com/very/long/path"}`
	resp, err := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("expected 201, got %d", resp.StatusCode)
	}

	var result map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		t.Fatal(err)
	}
	if result["short_url"] == "" {
		t.Fatal("expected short_url in response")
	}
	if result["original_url"] != "https://example.com/very/long/path" {
		t.Fatalf("expected original_url to be preserved, got %s", result["original_url"])
	}
}

func TestRedirect(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	// Create a short URL first
	body := `{"url": "https://example.com/redirect-target"}`
	resp, err := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatal(err)
	}
	var result map[string]string
	json.NewDecoder(resp.Body).Decode(&result)
	resp.Body.Close()

	shortURL := result["short_url"]
	// Extract the code from the short URL
	parts := strings.Split(shortURL, "/")
	code := parts[len(parts)-1]

	// Follow redirect
	client := &http.Client{CheckRedirect: func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse
	}}
	resp2, err := client.Get(srv.URL + "/" + code)
	if err != nil {
		t.Fatal(err)
	}
	defer resp2.Body.Close()

	if resp2.StatusCode != http.StatusFound && resp2.StatusCode != http.StatusMovedPermanently {
		t.Fatalf("expected redirect status, got %d", resp2.StatusCode)
	}
	if resp2.Header.Get("Location") != "https://example.com/redirect-target" {
		t.Fatalf("expected redirect to original URL, got %s", resp2.Header.Get("Location"))
	}
}

func TestShortenInvalidURL(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	body := `{"url": "not-a-valid-url"}`
	resp, err := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Fatalf("expected 400 for invalid URL, got %d", resp.StatusCode)
	}
}

func TestShortenEmptyBody(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	resp, err := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(""))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Fatalf("expected 400 for empty body, got %d", resp.StatusCode)
	}
}

func TestNotFoundCode(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/nonexistent")
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404 for unknown code, got %d", resp.StatusCode)
	}
}

func TestDuplicateURL(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	body := `{"url": "https://example.com/duplicate"}`
	resp1, _ := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	var result1 map[string]string
	json.NewDecoder(resp1.Body).Decode(&result1)
	resp1.Body.Close()

	resp2, _ := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	var result2 map[string]string
	json.NewDecoder(resp2.Body).Decode(&result2)
	resp2.Body.Close()

	if result1["short_url"] != result2["short_url"] {
		t.Fatal("same URL should return same short code")
	}
}

func TestListURLs(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	// Create some URLs
	for _, url := range []string{"https://a.com", "https://b.com", "https://c.com"} {
		body := `{"url": "` + url + `"}`
		resp, _ := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
		resp.Body.Close()
	}

	resp, err := http.Get(srv.URL + "/urls")
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}

	var urls []map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&urls); err != nil {
		t.Fatal(err)
	}
	if len(urls) < 3 {
		t.Fatalf("expected at least 3 URLs, got %d", len(urls))
	}
}

func TestHealthCheck(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/health")
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
}

func TestDeleteURL(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	// Create a URL
	body := `{"url": "https://example.com/to-delete"}`
	resp, _ := http.Post(srv.URL+"/shorten", "application/json", strings.NewReader(body))
	var result map[string]string
	json.NewDecoder(resp.Body).Decode(&result)
	resp.Body.Close()

	parts := strings.Split(result["short_url"], "/")
	code := parts[len(parts)-1]

	// Delete it
	req, _ := http.NewRequest("DELETE", srv.URL+"/"+code, nil)
	client := &http.Client{}
	resp2, err := client.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer resp2.Body.Close()

	if resp2.StatusCode != http.StatusNoContent && resp2.StatusCode != http.StatusOK {
		t.Fatalf("expected 204 or 200 on delete, got %d", resp2.StatusCode)
	}

	// Verify it's gone
	resp3, _ := http.Get(srv.URL + "/" + code)
	resp3.Body.Close()
	if resp3.StatusCode != http.StatusNotFound {
		t.Fatalf("expected 404 after delete, got %d", resp3.StatusCode)
	}
}

// newTestServer creates a test HTTP server with the URL shortener handler.
// The implementation must provide a function called NewHandler() http.Handler
// or newRouter() http.Handler that returns the application's HTTP handler.
func newTestServer(t *testing.T) *httptest.Server {
	t.Helper()
	handler := NewHandler()
	return httptest.NewServer(handler)
}
