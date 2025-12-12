
import sys
import os

# Add project root directory to path to allow importing fastapi_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from fastapi_server.main import app, get_db
from fastapi_server import models, schemas
from fastapi_server.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import pytest

# Create a test database
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = SessionLocal()
        # Override the bind to use our test in-memory db
        # Note: SessionLocal is configured with the original engine, so we need a new session factory or just bind
        # Actually simplest is to just create a new session with this engine
        db = Session(bind=engine)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_crud_flow():
    # 1. Register User 1
    user1_data = {"username": "user1", "email": "user1@example.com", "password": "password123"}
    response = client.post("/users/", json=user1_data)
    assert response.status_code == 200
    
    # 2. Login User 1
    response = client.post("/token", data={"username": "user1", "password": "password123"})
    assert response.status_code == 200
    token1 = response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 3. Create Post (User 1)
    post_data = {"caption": "First post"}
    response = client.post("/posts/", json=post_data, headers=headers1)
    assert response.status_code == 200
    post_id = response.json()["id"]
    
    # 4. Update Post (User 1)
    update_data = {"caption": "Updated caption"}
    response = client.put(f"/posts/{post_id}", json=update_data, headers=headers1)
    assert response.status_code == 200
    assert response.json()["caption"] == "Updated caption"
    
    # 5. Delete Post (User 1)
    response = client.delete(f"/posts/{post_id}", headers=headers1)
    assert response.status_code == 200
    
    # Verify Deletion
    # We don't have a GET /posts/{id} endpoint in the snippets I saw (only lists), but we can try to update it again
    response = client.put(f"/posts/{post_id}", json=update_data, headers=headers1)
    assert response.status_code == 404

    # 6. Create another post for comment testing
    response = client.post("/posts/", json={"caption": "Second post"}, headers=headers1)
    post2_id = response.json()["id"]

    # 7. Register & Login User 2
    user2_data = {"username": "user2", "email": "user2@example.com", "password": "password123"}
    client.post("/users/", json=user2_data)
    response = client.post("/token", data={"username": "user2", "password": "password123"})
    token2 = response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 8. User 2 comments on Post 2
    comment_data = {"content": "Nice post"}
    response = client.post(f"/posts/{post2_id}/comments/", json=comment_data, headers=headers2)
    assert response.status_code == 200
    comment_id = response.json()["id"]

    # 9. User 2 deletes their own comment
    response = client.delete(f"/comments/{comment_id}", headers=headers2)
    assert response.status_code == 200
    
    # 10. User 2 comments again
    response = client.post(f"/posts/{post2_id}/comments/", json={"content": "Another comment"}, headers=headers2)
    comment2_id = response.json()["id"]
    
    # 11. User 1 (Post owner) deletes User 2's comment
    response = client.delete(f"/comments/{comment2_id}", headers=headers1)
    assert response.status_code == 200

    print("All CRUD tests passed!")

if __name__ == "__main__":
    test_crud_flow()
