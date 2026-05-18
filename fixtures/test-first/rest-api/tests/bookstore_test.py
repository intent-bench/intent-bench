"""Test suite for the bookstore REST API.

The implementation must provide a Flask or FastAPI application
accessible via a test client. The app factory should be importable
as `from app import create_app` or `from main import create_app`.
"""

import pytest


@pytest.fixture
def client():
    """Create a test client for the bookstore API."""
    try:
        from app import create_app
    except ImportError:
        from main import create_app
    app = create_app(testing=True)
    if hasattr(app, "test_client"):
        # Flask
        with app.test_client() as c:
            yield c
    else:
        # FastAPI
        from fastapi.testclient import TestClient

        yield TestClient(app)


def get_json(resp):
    return resp.get_json() if hasattr(resp, "get_json") else resp.json()


def register_user(client, username="testuser", email="test@example.com", password="password123"):
    return client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def login_user(client, username="testuser", password="password123"):
    resp = client.post("/auth/login", json={"username": username, "password": password})
    data = get_json(resp)
    return data.get("token") or data.get("access_token")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_token(client):
    register_user(client, "viewer", "viewer@test.com", "pass123")
    return login_user(client, "viewer", "pass123")


@pytest.fixture
def admin_token(client):
    register_user(client, "admin", "admin@test.com", "pass123")
    token = login_user(client, "admin", "pass123")
    # Promote to admin -- implementation must seed an admin or provide a mechanism
    # Try direct promotion via bootstrap or existing admin
    return token


class TestAuth:
    def test_register(self, client):
        resp = register_user(client)
        assert resp.status_code in (200, 201)
        data = get_json(resp)
        assert data["username"] == "testuser"
        assert "password" not in data and "password_hash" not in data

    def test_register_duplicate(self, client):
        register_user(client)
        resp = register_user(client)
        assert resp.status_code in (400, 409, 422)

    def test_login(self, client):
        register_user(client)
        resp = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
        assert resp.status_code == 200
        data = get_json(resp)
        assert "token" in data or "access_token" in data

    def test_login_wrong_password(self, client):
        register_user(client)
        resp = client.post("/auth/login", json={"username": "testuser", "password": "wrong"})
        assert resp.status_code == 401

    def test_me(self, client, viewer_token):
        resp = client.get("/auth/me", headers=auth_header(viewer_token))
        assert resp.status_code == 200
        data = get_json(resp)
        assert data["username"] == "viewer"

    def test_me_no_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401


class TestBookCRUD:
    def test_create_book(self, client, admin_token):
        resp = client.post(
            "/books",
            json={
                "title": "Test Book",
                "author": "Author",
                "isbn": "9780131103627",
                "price": 29.99,
                "stock_quantity": 10,
            },
            headers=auth_header(admin_token),
        )
        assert resp.status_code in (200, 201)
        data = get_json(resp)
        assert data["title"] == "Test Book"
        assert "id" in data

    def test_get_book(self, client, admin_token):
        resp = client.post(
            "/books",
            json={
                "title": "Get Test",
                "author": "Author",
                "isbn": "9780132350884",
                "price": 19.99,
                "stock_quantity": 5,
            },
            headers=auth_header(admin_token),
        )
        data = get_json(resp)
        book_id = data["id"]

        resp2 = client.get(f"/books/{book_id}", headers=auth_header(admin_token))
        assert resp2.status_code == 200
        data2 = get_json(resp2)
        assert data2["title"] == "Get Test"

    def test_list_books(self, client, admin_token):
        for i in range(3):
            client.post(
                "/books",
                json={
                    "title": f"Book {i}",
                    "author": "Author",
                    "isbn": f"978013235088{i}",
                    "price": 10.0,
                    "stock_quantity": 1,
                },
                headers=auth_header(admin_token),
            )
        resp = client.get("/books", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = get_json(resp)
        items = data if isinstance(data, list) else data.get("items", data.get("books", []))
        assert len(items) >= 3

    def test_update_book(self, client, admin_token):
        resp = client.post(
            "/books",
            json={"title": "Original", "author": "Author", "isbn": "9780201633610", "price": 10.0, "stock_quantity": 1},
            headers=auth_header(admin_token),
        )
        book_id = get_json(resp)["id"]

        resp2 = client.put(f"/books/{book_id}", json={"title": "Updated"}, headers=auth_header(admin_token))
        assert resp2.status_code == 200
        assert get_json(resp2)["title"] == "Updated"

    def test_delete_book(self, client, admin_token):
        resp = client.post(
            "/books",
            json={
                "title": "To Delete",
                "author": "Author",
                "isbn": "9780596007126",
                "price": 10.0,
                "stock_quantity": 1,
            },
            headers=auth_header(admin_token),
        )
        book_id = get_json(resp)["id"]

        resp2 = client.delete(f"/books/{book_id}", headers=auth_header(admin_token))
        assert resp2.status_code in (200, 204)

        resp3 = client.get(f"/books/{book_id}", headers=auth_header(admin_token))
        assert resp3.status_code == 404

    def test_get_nonexistent_book(self, client, admin_token):
        resp = client.get("/books/99999", headers=auth_header(admin_token))
        assert resp.status_code == 404


class TestRBAC:
    def test_viewer_cannot_create(self, client, viewer_token):
        resp = client.post(
            "/books",
            json={"title": "Denied", "author": "Author", "isbn": "9780131103628", "price": 10.0, "stock_quantity": 1},
            headers=auth_header(viewer_token),
        )
        assert resp.status_code == 403

    def test_viewer_can_list(self, client, viewer_token):
        resp = client.get("/books", headers=auth_header(viewer_token))
        assert resp.status_code == 200

    def test_no_auth_rejected(self, client):
        resp = client.get("/books")
        assert resp.status_code == 401


class TestPagination:
    def test_default_pagination(self, client, admin_token):
        resp = client.get("/books?page=1", headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_per_page_param(self, client, admin_token):
        resp = client.get("/books?page=1&per_page=5", headers=auth_header(admin_token))
        assert resp.status_code == 200


class TestValidation:
    def test_invalid_isbn(self, client, admin_token):
        resp = client.post(
            "/books",
            json={"title": "Bad ISBN", "author": "Author", "isbn": "12345", "price": 10.0, "stock_quantity": 1},
            headers=auth_header(admin_token),
        )
        assert resp.status_code in (400, 422)

    def test_duplicate_isbn(self, client, admin_token):
        client.post(
            "/books",
            json={"title": "First", "author": "Author", "isbn": "9780131103629", "price": 10.0, "stock_quantity": 1},
            headers=auth_header(admin_token),
        )
        resp = client.post(
            "/books",
            json={"title": "Dupe", "author": "Author", "isbn": "9780131103629", "price": 10.0, "stock_quantity": 1},
            headers=auth_header(admin_token),
        )
        assert resp.status_code in (400, 409, 422)

    def test_missing_required_fields(self, client, admin_token):
        resp = client.post("/books", json={}, headers=auth_header(admin_token))
        assert resp.status_code in (400, 422)


class TestHealth:
    def test_health_no_auth(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
