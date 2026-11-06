# E-Learning FastAPI Example

A small e-learning course catalog API built with FastAPI. It demonstrates typed request/response models, validation, filtering, and generated Swagger UI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI, or `/redoc` for ReDoc.

## Example endpoints

```bash
# List all courses
curl http://127.0.0.1:8000/courses

# Filter courses
curl "http://127.0.0.1:8000/courses?level=beginner"

# Create a course
curl -X POST http://127.0.0.1:8000/courses \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI Essentials",
    "description": "Build APIs with FastAPI and interactive Swagger documentation.",
    "instructor": "Sam Lee",
    "level": "intermediate",
    "duration_hours": 8
  }'
```

Run tests with:

```bash
pytest
```
