# Bunath Pheng Portfolio API

FastAPI backend for the portfolio frontend at
[`BunathPheng/portfolio`](https://github.com/BunathPheng/portfolio). It exposes
the portfolio content used by the projects, skills, experience, education, and
contact sections.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/portfolio` | Return all frontend content in one response |
| `GET /api/projects` | List portfolio projects |
| `GET /api/projects/{id}` | Get one project |
| `GET /api/skills` | List skill groups |
| `GET /api/experience` | List work experience |
| `GET /api/education` | List education |
| `GET /api/social-links` | List social links |
| `POST /api/contact` | Validate and accept a contact form submission |

The contact endpoint accepts `name`, `email`, `subject`, `message`,
`website` (honeypot), and `turnstileToken`. It has a five-request-per-minute
per-IP limit. Set `TURNSTILE_SECRET_KEY` to enable Cloudflare Turnstile
verification; when it is not set, verification is skipped for local
development. Contact submissions are logged with a reference ID and should be
connected to an email or database provider for production delivery.

## Frontend integration

Set the frontend API base URL to the deployed backend and request
`GET /api/portfolio`. The response uses the frontend's existing camelCase keys
(`skillGroups`, `socialLinks`, `navItems`, `liveUrl`, and `githubUrl`).

For cross-origin deployments, set a comma-separated allowlist:

```bash
CORS_ORIGINS=https://your-portfolio.example
```

## Tests and Vercel

```bash
pytest
```

Vercel uses `api/index.py` as the Python function entrypoint. Its runtime
dependencies are listed in `api/requirements.txt`.
