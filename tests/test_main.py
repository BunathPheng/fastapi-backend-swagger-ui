from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "E-Learning Course Catalog" in response.text


def test_list_courses_and_filter_by_level() -> None:
    response = client.get("/courses?level=beginner")
    assert response.status_code == 200
    assert response.json()[0]["level"] == "beginner"


def test_create_course() -> None:
    response = client.post(
        "/courses",
        json={
            "title": "FastAPI Essentials",
            "description": "Build APIs with FastAPI and interactive Swagger documentation.",
            "instructor": "Sam Lee",
            "level": "intermediate",
            "duration_hours": 8,
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "FastAPI Essentials"


def test_course_validation() -> None:
    response = client.post("/courses", json={"title": "Too short"})
    assert response.status_code == 422


def test_missing_course() -> None:
    response = client.get("/courses/999999")
    assert response.status_code == 404
