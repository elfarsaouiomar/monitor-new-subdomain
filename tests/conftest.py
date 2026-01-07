import pytest
from pymongo import MongoClient
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.repository import repository


@pytest.fixture(scope="function")
def test_db():
    client = MongoClient("mongodb://localhost:27017")
    client.admin.command("ping")

    print(
        "Connected to MongoDB for testing",
        client.list_database_names(),
    )
    db = client["monitoring_test"]

    # Clean before each test
    db.domains.delete_many({})
    db.subdomains.delete_many({})

    yield db

    # Clean after each test
    db.domains.delete_many({})
    db.subdomains.delete_many({})


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        return test_db

    app.dependency_overrides[repository] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
