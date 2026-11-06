from fastapi.testclient import TestClient

from app.main import app, request_log


client = TestClient(app)


def setup_function() -> None:
    request_log.clear()


def test_health_check() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_portfolio_contains_frontend_sections() -> None:
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    body = response.json()
    assert len(body["projects"]) == 3
    assert len(body["skillGroups"]) == 4
    assert body["projects"][0]["githubUrl"] == "https://github.com/BunathPheng"


def test_project_detail_and_missing_project() -> None:
    response = client.get("/api/projects/2")
    assert response.status_code == 200
    assert response.json()["title"] == "SmartOps: Automation Platform"

    missing = client.get("/api/projects/999")
    assert missing.status_code == 404


def test_contact_submission() -> None:
    response = client.post(
        "/api/contact",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Project collaboration",
            "message": "I would like to discuss a project with you.",
        },
    )
    assert response.status_code == 202
    assert response.json()["accepted"] is True
    assert response.json()["reference"]


def test_contact_validation_and_honeypot() -> None:
    invalid = client.post("/api/contact", json={"name": "x", "email": "not-an-email"})
    assert invalid.status_code == 422

    honeypot = client.post(
        "/api/contact",
        json={
            "name": "Bot",
            "email": "bot@example.com",
            "subject": "Spam",
            "message": "This is a bot submission.",
            "website": "https://spam.example",
        },
    )
    assert honeypot.status_code == 202
    assert honeypot.json()["reference"] == "honeypot"


def test_contact_rate_limit() -> None:
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid contact message.",
    }
    for _ in range(5):
        assert client.post("/api/contact", json=payload).status_code == 202
    assert client.post("/api/contact", json=payload).status_code == 429
