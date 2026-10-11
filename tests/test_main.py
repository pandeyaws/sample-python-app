from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_returns_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>Sample Python App</title>" in response.text


def test_status_endpoint_returns_application_status() -> None:
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Hello from Python on AKS",
        "status": "running",
    }


def test_health_endpoint_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_unknown_route_returns_not_found() -> None:
    response = client.get("/missing")

    assert response.status_code == 404
