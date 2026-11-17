"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
def test_list_books_empty(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == [] 

def test_get_invalid_book(client):
    response = client.get("/books/9999")
    body = response.get_json()

    assert response.status_code == 404
    assert body["code"] == "NOT_FOUND"

def test_post_with_only_author(client):
    response = client.post("/books", json = {"author": "Xuan Tuong"})
    body = response.get_json()

    assert response.status_code == 400
    error_fields = [item["field"] for item in body.get("errors", [])]
    assert "title" in error_fields 

def test_post_and_delete(client):
    create_resp = client.post("/books", json={"title": "Clean Code", "author": "Robert C. Martin"})
    assert create_resp.status_code == 201
    
    book_id = create_resp.get_json()["id"]
    
    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204 

    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404
    assert get_resp.get_json()["code"] == "NOT_FOUND"
