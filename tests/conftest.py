from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.auth.middleware import JWTAuthMiddleware
from src.database import Base, get_db
from src.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# The JWT middleware creates its own DB sessions, so we override its factory too
for _m in app.user_middleware:
    if _m.cls is JWTAuthMiddleware:
        _m.kwargs["session_factory"] = TestingSessionLocal  # ty: ignore[invalid-assignment]
        break
app.middleware_stack = None


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Signup + login, returns auth header."""
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    resp = client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
