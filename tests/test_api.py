def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_list_domains(client):
    response = client.get("/api/v1/domains")

    assert response.status_code == 200
    assert "domains" in response.json()
    assert "total" in response.json()


def test_list_subdomains(client):
    domain = "google.fr"
    add_response = client.post(
        "/api/v1/domains",
        json={
            "domain": domain,
            "notify_slack": False,
            "notify_telegram": False,
        },
    )

    assert add_response.status_code == 201

    response = client.get(f"api/v1/domains/{domain}/subdomains")

    assert response.status_code == 200
    assert isinstance(response.json()["subdomains"], list)
