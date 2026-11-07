from fastapi.testclient import TestClient

import app.main as main


class FakeRepository:
    configured = True

    def __init__(self) -> None:
        self.saved_contacts: list[dict] = []

    async def list_rows(self, table: str) -> list[dict]:
        rows = {
            "projects": [
                {
                    "id": 1,
                    "title": "SmartOps: Automation Platform",
                    "category": "DevOps",
                    "image": "Final.png",
                    "problem": "A deployment problem.",
                    "solution": "An automated solution.",
                    "architecture": "A platform architecture.",
                    "contribution": ["Built pipelines"],
                    "results": ["Reliable releases"],
                    "technologies": ["Docker"],
                    "live_url": "#",
                    "github_url": "https://github.com/BunathPheng",
                }
            ],
            "skill_groups": [{"category": "DevOps & Cloud", "icon": "cloud", "skills": ["Docker"]}],
            "experiences": [
                {
                    "title": "DevOps Engineer",
                    "company": "KSHRD",
                    "location": "Phnom Penh",
                    "period": "2025",
                    "description": "Built deployment automation.",
                    "technologies": ["Docker"],
                }
            ],
            "education": [
                {
                    "degree": "Bachelor",
                    "field": "Computer Science",
                    "school": "RUPP",
                    "period": "Present",
                    "description": "Software engineering studies.",
                }
            ],
            "social_links": [{"label": "GitHub", "href": "https://github.com/BunathPheng"}],
            "nav_items": [{"label": "Projects", "href": "#projects"}],
        }
        return rows[table]

    async def get_row(self, table: str, row_id: int) -> dict | None:
        rows = await self.list_rows(table)
        return next((row for row in rows if row.get("id") == row_id), None)

    async def create_contact(self, payload: dict) -> dict:
        self.saved_contacts.append(payload)
        return payload


client = TestClient(main.app)


def setup_function() -> None:
    main.request_log.clear()
    main.repository = FakeRepository()


def test_health_check() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["database_configured"] is True


def test_portfolio_comes_from_database_tables() -> None:
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    body = response.json()
    assert body["projects"][0]["title"] == "SmartOps: Automation Platform"
    assert body["skillGroups"][0]["skills"] == ["Docker"]
    assert body["navItems"][0]["href"] == "#projects"


def test_project_detail_and_missing_project() -> None:
    response = client.get("/api/projects/1")
    assert response.status_code == 200
    assert response.json()["githubUrl"] == "https://github.com/BunathPheng"

    missing = client.get("/api/projects/999")
    assert missing.status_code == 404


def test_contact_submission_is_saved() -> None:
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
    assert len(main.repository.saved_contacts) == 1


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
