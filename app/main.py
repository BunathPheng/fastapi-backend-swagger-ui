import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated, Literal

import httpx
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class PortfolioResponse(BaseModel):
    projects: list[Project]
    skill_groups: list[SkillGroup] = Field(alias="skillGroups")
    experiences: list[Experience]
    education: list[Education]
    social_links: list[SocialLink] = Field(alias="socialLinks")
    nav_items: list[SocialLink] = Field(alias="navItems")

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


projects = [
    Project(
        id=1,
        title="English Club: E-Learning Management System",
        category="Full-Stack",
        image="English.jpg",
        problem="Learners needed a unified platform to register, access courses, take quizzes, and track progress—without fragmented tools or insecure access.",
        solution="Built an end-to-end learning platform with JWT-authenticated REST APIs, role-aware dashboards, and a responsive Next.js frontend for seamless course consumption.",
        architecture="Next.js frontend with NextAuth JWT sessions, RESTful API integration, server-side rendering for performance, and modular page routing for courses, quizzes, and progress tracking.",
        contribution=["Integrated frontend with backend RESTful APIs and ensured smooth data flow", "Implemented JWT authentication with NextAuth", "Built user onboarding, course consumption, and progress tracking flows", "Collaborated with backend team on API contracts and error handling"],
        results=["Complete E2E learning flow from registration to progress tracking", "Secure authenticated access across all user journeys", "Responsive UI built with TypeScript and Tailwind CSS"],
        technologies=["Next.js", "TypeScript", "Tailwind CSS", "REST APIs", "JWT", "NextAuth"],
        liveUrl="#",
        githubUrl="https://github.com/BunathPheng",
    ),
    Project(
        id=2,
        title="SmartOps: Automation Platform",
        category="DevOps",
        image="Final.png",
        problem="Manual deployments were slow, error-prone, and lacked traceability from source code to production environments.",
        solution="Designed a GitOps-first automation platform covering the full deployment lifecycle with CI/CD pipelines, container orchestration, and infrastructure as code.",
        architecture="Jenkins and GitHub Actions for CI, Argo CD for GitOps delivery, Docker/Kubernetes for runtime, Ansible for provisioning, and Prometheus/Grafana for observability.",
        contribution=["Built CI/CD pipelines with Jenkins and GitHub Actions", "Implemented GitOps workflows with Argo CD", "Containerized workloads and deployed on Kubernetes", "Automated infrastructure provisioning with Ansible"],
        results=["Automated deployment lifecycle from repo to production", "Faster, more reliable releases with full traceability", "Reduced manual intervention and deployment risk"],
        technologies=["Jenkins", "GitHub Actions", "Argo CD", "Docker", "Kubernetes", "Ansible", "Prometheus", "Grafana"],
        liveUrl="#",
        githubUrl="https://github.com/BunathPheng",
    ),
    Project(
        id=3,
        title="Selamounty: Digital Cultural & Educational Hub",
        category="Platform",
        image="selamonty.png",
        problem="Cultural institutions needed a scalable digital platform to deliver rich media content and educational experiences to a global audience.",
        solution="Delivered backend services and deployment automation for a virtual museum platform with resilient APIs and automated rollouts.",
        architecture="Spring Boot microservices with MySQL persistence, Jenkins CI/CD pipelines, Docker containerization, and Nginx reverse proxy for production traffic.",
        contribution=["Built and maintained Spring Boot API services", "Set up automated deployment pipelines with Jenkins and Docker", "Configured Nginx for production traffic routing", "Ensured reliable rollout for media-rich experiences"],
        results=["Scalable platform serving global visitors", "Automated deployments with minimal downtime", "Reliable API layer for content delivery"],
        technologies=["Java", "Spring Boot", "MySQL", "Jenkins", "Docker", "Nginx"],
        liveUrl="#",
        githubUrl="https://github.com/BunathPheng",
    ),
]

skill_groups = [
    SkillGroup(category="DevOps & Cloud", icon="cloud", skills=["Docker", "Kubernetes", "Helm", "Jenkins", "Argo CD", "Ansible", "GitHub Actions", "Prometheus", "Grafana"]),
    SkillGroup(category="Frontend", icon="layout", skills=["React", "Next.js", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind CSS"]),
    SkillGroup(category="Backend & Data", icon="database", skills=["Spring Boot", "Java", "PostgreSQL", "MySQL", "REST APIs", "JWT"]),
    SkillGroup(category="Tools & Design", icon="tool", skills=["Git", "Linux", "Nginx", "Figma"]),
]

experiences = [
    Experience(title="DevOps Engineer – SmartOps Automation Platform", company="Korea Software HRD Center", location="Phnom Penh, Cambodia", period="2025", description="Built an automated platform covering the full deployment lifecycle—from repo to production—using GitOps and CI/CD to simplify, speed up, and de-risk releases.", technologies=["Jenkins", "GitHub Actions", "Argo CD", "Docker", "Kubernetes", "Ansible", "Prometheus", "Grafana"]),
    Experience(title="Backend / Platform Engineer – Selamounty", company="Korea Software HRD Center", location="Phnom Penh, Cambodia", period="2025", description="Delivered a digital cultural and educational platform with automated deployments, API services, and resilient runtime for global visitors.", technologies=["Java", "Spring Boot", "MySQL", "Jenkins", "Docker", "Nginx"]),
    Experience(title="Front-End Developer – English Club Platform", company="Institute of Science and Technology Advanced Development", location="Phnom Penh, Cambodia", period="2024", description="Built an education platform enabling learners to practice English with authenticated user flows and dashboards.", technologies=["Next.js", "TypeScript", "JWT", "REST APIs", "Tailwind CSS"]),
]

education = [
    Education(degree="Bachelor of Computer Science", field="Royal University of Phnom Penh (RUPP)", school="Royal University of Phnom Penh", period="Jan 2022 – Present", description="Comprehensive CS curriculum with focus on software engineering and systems."),
    Education(degree="Advanced Course: DevOps", field="Korea Software HRD Center (KSHRD)", school="Korea Software HRD Center", period="Jul – Dec 2025", description="Modern CI/CD, containerization, cloud infrastructure, GitOps with Jenkins, GitHub Actions, Argo CD, Docker, and Kubernetes."),
    Education(degree="Basic Course Training", field="Korea Software HRD Center (KSHRD)", school="Korea Software HRD Center", period="Feb – Jul 2025", description="Foundation across Linux, Docker, Git, UI/UX, Java, HTML/CSS/JS, Tailwind CSS, PostgreSQL, and responsive web apps."),
    Education(degree="Foundation 2 Generation", field="Institute of Science and Technology Advanced Development (ISTAD)", school="ISTAD", period="Jan 2025 – Present", description="Core software engineering foundations and collaborative projects."),
]

social_links = [
    SocialLink(label="LinkedIn", href="https://www.linkedin.com/in/bunath-pheng-71a41b318"),
    SocialLink(label="GitHub", href="https://github.com/BunathPheng"),
    SocialLink(label="Telegram", href="https://t.me/pheng_bunath"),
    SocialLink(label="Facebook", href="https://web.facebook.com/profile.php?id=100027603155423"),
]

nav_items = [
    SocialLink(label="About", href="#about"),
    SocialLink(label="Skills", href="#skills"),
    SocialLink(label="Projects", href="#projects"),
    SocialLink(label="Experience", href="#experience"),
    SocialLink(label="Education", href="#education"),
    SocialLink(label="Contact", href="#contact"),
]

app = FastAPI(
    title="Bunath Pheng Portfolio API",
    description="Content and contact API for Bunath Pheng's portfolio frontend.",
    version="1.0.0",
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


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {"message": "Bunath Pheng Portfolio API is running", "docs": "/docs"}


@app.get("/api/portfolio", response_model=PortfolioResponse, tags=["portfolio"])
def get_portfolio() -> PortfolioResponse:
    return PortfolioResponse(
        projects=projects,
        skillGroups=skill_groups,
        experiences=experiences,
        education=education,
        socialLinks=social_links,
        navItems=nav_items,
    )


@app.get("/api/projects", response_model=list[Project], tags=["portfolio"])
def list_projects() -> list[Project]:
    return projects


@app.get("/api/projects/{project_id}", response_model=Project, tags=["portfolio"])
def get_project(project_id: int) -> Project:
    project = next((item for item in projects if item.id == project_id), None)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/api/skills", response_model=list[SkillGroup], tags=["portfolio"])
def list_skills() -> list[SkillGroup]:
    return skill_groups


@app.get("/api/experience", response_model=list[Experience], tags=["portfolio"])
def list_experience() -> list[Experience]:
    return experiences


@app.get("/api/education", response_model=list[Education], tags=["portfolio"])
def list_education() -> list[Education]:
    return education


@app.get("/api/social-links", response_model=list[SocialLink], tags=["portfolio"])
def list_social_links() -> list[SocialLink]:
    return social_links


def _client_ip(request: Request) -> str:
    return request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0].strip()


def _rate_limit(ip: str, limit: int = 5, window_seconds: int = 60) -> bool:
    now = time.monotonic()
    recent = [timestamp for timestamp in request_log.get(ip, []) if now - timestamp < window_seconds]
    if len(recent) >= limit:
        request_log[ip] = recent
        return False
    recent.append(now)
    request_log[ip] = recent
    return True


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
    received_at = datetime.now(timezone.utc).isoformat()
    print(f"contact_submission reference={reference} received_at={received_at} subject={payload.subject!r}")
    return ContactResponse(accepted=True, message="Message received. I will get back to you soon.", reference=reference)
