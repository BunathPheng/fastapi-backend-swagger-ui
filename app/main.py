from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field


class Course(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Python for Beginners",
                    "description": "Learn Python fundamentals through practical exercises.",
                    "instructor": "Alex Johnson",
                    "level": "beginner",
                    "duration_hours": 12,
                }
            ]
        }
    )

    id: int = Field(description="Unique course identifier", examples=[1])
    title: str = Field(min_length=3, max_length=100, examples=["Python for Beginners"])
    description: str = Field(min_length=10, max_length=500)
    instructor: str = Field(min_length=2, max_length=100)
    level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    duration_hours: int = Field(gt=0, le=500, examples=[12])


class CourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100, examples=["Python for Beginners"])
    description: str = Field(min_length=10, max_length=500)
    instructor: str = Field(min_length=2, max_length=100)
    level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    duration_hours: int = Field(gt=0, le=500, examples=[12])


app = FastAPI(
    title="E-Learning API",
    description="A simple course catalog API for an e-learning platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

courses: list[Course] = [
    Course(
        id=1,
        title="Python for Beginners",
        description="Learn Python fundamentals through practical exercises.",
        instructor="Alex Johnson",
        level="beginner",
        duration_hours=12,
    )
]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def course_catalog_ui() -> str:
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>E-Learning Course Catalog</title>
    <style>
      :root { color-scheme: light; font-family: Inter, system-ui, sans-serif; }
      body { margin: 0; background: #f4f7fb; color: #172033; }
      header { padding: 48px 24px; background: #173b73; color: white; }
      main { max-width: 960px; margin: 0 auto; padding: 28px 24px; }
      .eyebrow { margin: 0 0 8px; color: #9dc3ff; font-weight: 700; }
      h1 { margin: 0; font-size: clamp(2rem, 5vw, 3.5rem); }
      .toolbar { display: flex; gap: 12px; margin-bottom: 24px; }
      select, button { border: 1px solid #c9d3e2; border-radius: 8px; padding: 10px 12px; font: inherit; }
      button { cursor: pointer; background: #2166d1; color: white; border: 0; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; }
      .card { padding: 20px; background: white; border: 1px solid #e1e7f0; border-radius: 12px; box-shadow: 0 5px 16px #173b7312; }
      .card h2 { margin: 0 0 10px; font-size: 1.2rem; }
      .meta { color: #52627a; font-size: .9rem; }
      .error { color: #a42626; }
      nav { margin-top: 16px; }
      nav a { color: #cfe0ff; margin-right: 16px; }
    </style>
  </head>
  <body>
    <header>
      <main>
        <p class="eyebrow">E-LEARNING PLATFORM</p>
        <h1>Learn something useful today.</h1>
        <nav><a href="/docs">API documentation</a><a href="/redoc">ReDoc</a></nav>
      </main>
    </header>
    <main>
      <div class="toolbar">
        <select id="level" aria-label="Filter by level">
          <option value="">All levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        <button id="refresh">Refresh courses</button>
      </div>
      <section id="courses" class="grid" aria-live="polite"></section>
    </main>
    <script>
      const container = document.querySelector("#courses");
      const level = document.querySelector("#level");
      async function loadCourses() {
        container.innerHTML = "<p>Loading courses...</p>";
        const query = level.value ? `?level=${encodeURIComponent(level.value)}` : "";
        try {
          const response = await fetch(`/courses${query}`);
          if (!response.ok) throw new Error("Unable to load courses.");
          const courses = await response.json();
          container.innerHTML = courses.length ? courses.map(course => `
            <article class="card">
              <h2>${course.title}</h2>
              <p>${course.description}</p>
              <p class="meta">${course.instructor} · ${course.level} · ${course.duration_hours} hours</p>
            </article>
          `).join("") : "<p>No courses match this filter.</p>";
        } catch (error) {
          container.innerHTML = `<p class="error">${error.message}</p>`;
        }
      }
      level.addEventListener("change", loadCourses);
      document.querySelector("#refresh").addEventListener("click", loadCourses);
      loadCourses();
    </script>
  </body>
</html>"""


@app.get("/courses", response_model=list[Course], tags=["courses"])
def list_courses(
    level: Annotated[
        str | None,
        Query(
            description="Optional course level filter",
            pattern="^(beginner|intermediate|advanced)$",
        ),
    ] = None,
) -> list[Course]:
    if level is None:
        return courses
    return [course for course in courses if course.level == level]


@app.post(
    "/courses",
    response_model=Course,
    status_code=status.HTTP_201_CREATED,
    tags=["courses"],
)
def create_course(course_data: CourseCreate) -> Course:
    course = Course(id=max((item.id for item in courses), default=0) + 1, **course_data.model_dump())
    courses.append(course)
    return course


@app.get("/courses/{course_id}", response_model=Course, tags=["courses"])
def get_course(course_id: int) -> Course:
    for course in courses:
        if course.id == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")
