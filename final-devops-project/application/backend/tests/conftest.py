"""Test setup: every test uses a fresh SQLite database, never PostgreSQL."""
import os

# Must be set before the app is imported, so the app's engine points at SQLite
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def product(client):
    """A product that already exists, for tests that need one."""
    response = client.post(
        "/api/products",
        json={"name": "USB-C Cable", "sku": "CAB-001", "category": "Accessories",
              "quantity": 25, "price": 9.99, "reorder_level": 10},
    )
    assert response.status_code == 201
    return response.json()
