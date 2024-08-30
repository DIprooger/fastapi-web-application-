import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api import app, get_db
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
print(f"Using database: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
def setup_and_teardown_db():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"

def test_create_user_duplicate():
    client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 400

def test_login_for_access_token():
    client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_create_note():
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200

    token_response = client.post(
        "/token",
        data={"username": "testuser@example.com", "password": "password123"}
    )
    assert token_response.status_code == 200
    data = token_response.json()
    access_token = data.get("access_token")
    print(f"Access Token: {access_token}")
    assert access_token is not None

    response = client.post(
        "/notes/",
        json={
            "title": "Test Note", "content": "This is a test note"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Create Note Response: {response.status_code}, {response.json()}")
    assert response.status_code == 200

def test_delete_user():
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    response = client.delete(f"/users/1")
    assert response.status_code == 200
    response = client.delete(f"/users/1")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Note with id 1 not found'}
