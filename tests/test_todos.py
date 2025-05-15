import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from database import SessionLocal, init_db, TEST_DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos"))
        conn.execute(text("DELETE FROM users"))
        conn.commit()
    yield
    engine.dispose()

def test_todo_crud():
    client.post("/users/signup", json={"email": "test@example.com", "password": "password123"})
    login_response = client.post("/users/login", json={"email": "test@example.com", "password": "password123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post(
        "/todos",
        json={"title": "Test Todo", "description": "Test description", "completed": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    todo_id = response.json()["id"]
    assert response.json()["title"] == "Test Todo"

    response = client.get("/todos", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Todo"

    response = client.get(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"

    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated Todo", "description": "Updated description", "completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Todo"
    assert response.json()["completed"] is True

    response = client.delete(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.get(f"/todos/{todo_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_search_todos():
    client.post("/users/signup", json={"email": "search@example.com", "password": "password123"})
    login_response = client.post("/users/login", json={"email": "search@example.com", "password": "password123"})
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    token = login_response.json()["access_token"]

    response = client.post(
        "/todos",
        json={"title": "Test Todo", "description": "Test", "completed": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Create todo failed: {response.json()}"

    response = client.post(
        "/todos",
        json={"title": "Another Task", "description": "Different", "completed": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Create another todo failed: {response.json()}"

    response = client.get("/todos/search?q=Test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Search failed: {response.json()}"
    assert len(response.json()) == 1, f"Expected 1 todo, got {len(response.json())}"
    assert response.json()[0]["title"] == "Test Todo"

def test_unauthorized_todo_access():
    response = client.get("/todos")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_invalid_todo_id():
    client.post("/users/signup", json={"email": "test@example.com", "password": "password123"})
    login_response = client.post("/users/login", json={"email": "test@example.com", "password": "password123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get("/todos/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"
