import os
import time
import uuid
import asyncio
from typing import Annotated, Literal

import httpx
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.database import DatabaseUnavailable, repository


class Project(BaseModel):
    id: int
    title: str
    category: str
    image: str
    problem: str
    solution: str
    architecture: str
    contribution: list[str]
    results: list[str]
    technologies: list[str]
    live_url: str = Field(alias="liveUrl")
    github_url: str = Field(alias="githubUrl")
    model_config = ConfigDict(populate_by_name=True)


class SkillGroup(BaseModel):
    category: str
    icon: Literal["cloud", "layout", "database", "tool"]
    skills: list[str]


class Experience(BaseModel):
    title: str
    company: str
    location: str
    period: str
    description: str
    technologies: list[str]


class Education(BaseModel):
    degree: str
    field: str
    school: str
    period: str
    description: str


class SocialLink(BaseModel):
    label: str
    href: str


class DevOpsStage(BaseModel):
    step: str
    title: str
    description: str
    image: str
    color: str


class PortfolioResponse(BaseModel):
    projects: list[Project]
    skill_groups: list[SkillGroup] = Field(alias="skillGroups")
    experiences: list[Experience]
    education: list[Education]
    social_links: list[SocialLink] = Field(alias="socialLinks")
    nav_items: list[SocialLink] = Field(alias="navItems")
    devops_lifecycle: list[DevOpsStage] = Field(alias="devopsLifecycle")
    model_config = ConfigDict(populate_by_name=True)


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    website: str = Field(default="", max_length=200)
    turnstile_token: str = Field(default="", alias="turnstileToken")
    model_config = ConfigDict(populate_by_name=True)


class ContactResponse(BaseModel):
    accepted: bool
    message: str
    reference: str


app = FastAPI(
    title="Bunath Pheng Portfolio API",
    description="Supabase-backed content and contact API for Bunath Pheng's portfolio frontend.",
    version="2.0.0",
)

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

request_log: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    return request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "unknown"
    ).split(",")[0].strip()


def _rate_limit(ip: str, limit: int = 5, window_seconds: int = 60) -> bool:
    now = time.monotonic()
    recent = [timestamp for timestamp in request_log.get(ip, []) if now - timestamp < window_seconds]
    if len(recent) >= limit:
        request_log[ip] = recent
        return False
    recent.append(now)
    request_log[ip] = recent
    return True


def _database_error(error: DatabaseUnavailable) -> HTTPException:
    return HTTPException(status_code=503, detail=str(error))


async def _rows(table: str) -> list[dict]:
    try:
        return await repository.list_rows(table)
    except DatabaseUnavailable as error:
        raise _database_error(error) from error


def _project(row: dict) -> Project:
    return Project(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        image=row["image"],
        problem=row["problem"],
        solution=row["solution"],
        architecture=row["architecture"],
        contribution=row.get("contribution", []),
        results=row.get("results", []),
        technologies=row.get("technologies", []),
        liveUrl=row["live_url"],
        githubUrl=row["github_url"],
    )


def _skill_group(row: dict) -> SkillGroup:
    return SkillGroup(category=row["category"], icon=row["icon"], skills=row.get("skills", []))


def _experience(row: dict) -> Experience:
    return Experience(
        title=row["title"],
        company=row["company"],
        location=row["location"],
        period=row["period"],
        description=row["description"],
        technologies=row.get("technologies", []),
    )


def _education(row: dict) -> Education:
    return Education(
        degree=row["degree"],
        field=row["field"],
        school=row["school"],
        period=row["period"],
        description=row["description"],
    )


def _link(row: dict) -> SocialLink:
    return SocialLink(label=row["label"], href=row["href"])


def _devops_stage(row: dict) -> DevOpsStage:
    return DevOpsStage(
        step=row["step"],
        title=row["title"],
        description=row["description"],
        image=row["image"],
        color=row["color"],
    )


@app.get("/", tags=["health"])
def health_check() -> dict[str, str | bool]:
    return {
        "message": "Bunath Pheng Portfolio API is running",
        "docs": "/docs",
        "database_configured": repository.configured,
    }


@app.get("/api/portfolio", response_model=PortfolioResponse, tags=["portfolio"])
async def get_portfolio() -> PortfolioResponse:
    projects, skills, experience, education, social, nav, lifecycle = await asyncio.gather(
        _rows("projects"),
        _rows("skill_groups"),
        _rows("experiences"),
        _rows("education"),
        _rows("social_links"),
        _rows("nav_items"),
        _rows("devops_lifecycle"),
    )
    return PortfolioResponse(
        projects=[_project(row) for row in projects],
        skillGroups=[_skill_group(row) for row in skills],
        experiences=[_experience(row) for row in experience],
        education=[_education(row) for row in education],
        socialLinks=[_link(row) for row in social],
        navItems=[_link(row) for row in nav],
        devopsLifecycle=[_devops_stage(row) for row in lifecycle],
    )


@app.get("/api/devops-lifecycle", response_model=list[DevOpsStage], tags=["portfolio"])
async def list_devops_lifecycle() -> list[DevOpsStage]:
    return [_devops_stage(row) for row in await _rows("devops_lifecycle")]


@app.get("/api/projects", response_model=list[Project], tags=["portfolio"])
async def list_projects() -> list[Project]:
    return [_project(row) for row in await _rows("projects")]


@app.get("/api/projects/{project_id}", response_model=Project, tags=["portfolio"])
async def get_project(project_id: int) -> Project:
    try:
        row = await repository.get_row("projects", project_id)
    except DatabaseUnavailable as error:
        raise _database_error(error) from error
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project(row)


@app.get("/api/skills", response_model=list[SkillGroup], tags=["portfolio"])
async def list_skills() -> list[SkillGroup]:
    return [_skill_group(row) for row in await _rows("skill_groups")]


@app.get("/api/experience", response_model=list[Experience], tags=["portfolio"])
async def list_experience() -> list[Experience]:
    return [_experience(row) for row in await _rows("experiences")]


@app.get("/api/education", response_model=list[Education], tags=["portfolio"])
async def list_education() -> list[Education]:
    return [_education(row) for row in await _rows("education")]


@app.get("/api/social-links", response_model=list[SocialLink], tags=["portfolio"])
async def list_social_links() -> list[SocialLink]:
    return [_link(row) for row in await _rows("social_links")]


async def _verify_turnstile(token: str, ip: str) -> bool:
    secret = os.getenv("TURNSTILE_SECRET_KEY", "").strip()
    if not secret:
        return True
    if not token:
        return False
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": secret, "response": token, "remoteip": ip},
        )
    return response.is_success and bool(response.json().get("success"))


@app.post(
    "/api/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["contact"],
)
async def submit_contact(
    payload: ContactRequest,
    request: Request,
    x_forwarded_for: Annotated[str | None, Header()] = None,
) -> ContactResponse:
    ip = (x_forwarded_for or _client_ip(request)).split(",")[0].strip()
    if not _rate_limit(ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute and try again.")
    if payload.website.strip():
        return ContactResponse(accepted=True, message="Message received.", reference="honeypot")
    if not await _verify_turnstile(payload.turnstile_token.strip(), ip):
        raise HTTPException(status_code=400, detail="Cloudflare verification failed. Please try again.")

    reference = uuid.uuid4().hex[:12]
    try:
        await repository.create_contact(
            {
                "reference": reference,
                "name": payload.name.strip(),
                "email": str(payload.email),
                "subject": payload.subject.strip(),
                "message": payload.message.strip(),
                "ip_address": ip,
            }
        )
    except DatabaseUnavailable as error:
        raise _database_error(error) from error
    return ContactResponse(
        accepted=True,
        message="Message received. I will get back to you soon.",
        reference=reference,
    )
