import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    client.post("/api/auth/signup", json={"name": "Test User", "email": "test@example.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client):
    """Register a second user and return auth headers."""
    client.post("/api/auth/signup", json={"name": "Second User", "email": "second@example.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "second@example.com", "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
