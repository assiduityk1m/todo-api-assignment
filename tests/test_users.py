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

def test_signup_and_login():
    response = client.post("/users/signup", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    response = client.post("/users/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_unauthorized_access():
    response = client.get("/users/me")
    assert response.status_code == 401

def test_update_user():
    client.post("/users/signup", json={"email": "test2@example.com", "password": "password123"})
    login_response = client.post("/users/login", json={"email": "test2@example.com", "password": "password123"})
    token = login_response.json()["access_token"]

    response = client.put("/users/me", json={"email": "updated@example.com"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"