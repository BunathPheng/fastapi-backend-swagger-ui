from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
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
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    instructor: str = Field(min_length=2, max_length=100)
    level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    duration_hours: int = Field(gt=0, le=500)


class CourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    instructor: str = Field(min_length=2, max_length=100)
    level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    duration_hours: int = Field(gt=0, le=500)


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


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {"message": "E-Learning API is running", "docs": "/docs"}


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
    course = Course(
        id=max((item.id for item in courses), default=0) + 1,
        **course_data.model_dump(),
    )
    courses.append(course)
    return course


@app.get("/courses/{course_id}", response_model=Course, tags=["courses"])
def get_course(course_id: int) -> Course:
    for course in courses:
        if course.id == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")
