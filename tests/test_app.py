import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient

from .context import src

app = src.API.create_app()

testclient = TestClient(app)

# Mocking the MongoClient for testing
@pytest.fixture
def mock_mongo_client(monkeypatch):
    def mock_mongo_client_fn(*args, **kwargs):
        return MongoClient()

    monkeypatch.setattr("pymongo.MongoClient", mock_mongo_client_fn)


def test_ping():
    response = testclient.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"success": True, "code": 200, "message": "pong"}


def test_list_domains():
    response = testclient.get("/api/v1/domains")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(response.json()["message"], list)


def test_add_new_domain():
    domain_name = "heckerone.com"
    response = testclient.post("/api/v1/domain",
                                params={
                                    "domain": domain_name
                                    }
                            )
    print(response.url)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["message"] == domain_name

    # Test adding a duplicate domain
    response = testclient.post(url="/api/v1/domain", 
                               params={
                                   "domain": domain_name
                                })
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["message"] == "Domain already exists"


def test_get_subdomains_by_domain():
    domain_name = "heckerone.com"

    # Test getting subdomains for an existing domain
    response = testclient.get(f"/api/v1/subdomains/{domain_name}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(response.json()["message"], dict)

    # Test getting subdomains for a non-existent domain
    response = testclient.get("/api/v1/subdomains/non_existent_domain")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "not found"


def test_delete_domain():
    domain_name = "heckerone.com"

    # Test deleting an existing domain
    response = testclient.delete(f"/api/v1/domain/{domain_name}")
    assert response.status_code == 204
    assert response.json()["success"] is True
    assert response.json()["message"] == "domain deleted successfully"

    # Test deleting a non-existent domain
    response = testclient.delete("/api/v1/domain/example.com")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["message"] == "not found"


def test_monitor():
    response = testclient.get("/api/v1/monitor")
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["message"] == "start Monitoring"


