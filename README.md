# Bunath Pheng Portfolio API

FastAPI + Supabase backend for the portfolio frontend at
[`BunathPheng/portfolio`](https://github.com/BunathPheng/portfolio). It exposes
the portfolio content used by the projects, skills, experience, education, and
contact sections. Content is stored in PostgreSQL through Supabase; the API no
longer uses in-memory portfolio data.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

## Supabase setup

1. Create a Supabase project.
2. Open **SQL Editor** and run `supabase/migrations/001_portfolio.sql`.
3. Run `supabase/seed.sql` once to load the current portfolio content.
4. Add these Vercel environment variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SECRET_KEY=your-server-only-secret-key
CORS_ORIGINS=https://your-portfolio-domain.vercel.app
```

`SUPABASE_ANON_KEY` is used for Supabase Auth password login and access-token
verification. Keep `SUPABASE_SECRET_KEY` server-only; never put it in the
frontend or expose it as a `NEXT_PUBLIC_*` variable.
`SUPABASE_SERVICE_ROLE_KEY` remains supported for older Supabase projects.

The schema uses separate tables for each portfolio section and PostgreSQL
`text[]` columns for ordered lists such as skills, technologies, contributions,
and results. `contact_submissions` stores validated messages with a reference,
IP address, status, and timestamp. Row Level Security is enabled on every
table; the FastAPI service uses the server-side service role to access them.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /api/auth/login` | Sign in with a Supabase Auth email and password |
| `GET /api/auth/me` | Return the authenticated Supabase user |
| `GET /api/portfolio` | Return all frontend content in one response |
| `GET /api/projects` | List portfolio projects |
| `GET /api/projects/{id}` | Get one project |
| `GET /api/skills` | List skill groups |
| `GET /api/experience` | List work experience |
| `GET /api/education` | List education |
| `GET /api/social-links` | List social links |
| `GET /api/devops-lifecycle` | List the DevOps delivery sequence |
| `POST /api/contact` | Validate and save a contact form submission |

The contact endpoint accepts `name`, `email`, `subject`, `message`,
`website` (honeypot), and `turnstileToken`. It has a five-request-per-minute
per-IP limit. Set `TURNSTILE_SECRET_KEY` to enable Cloudflare Turnstile
verification; when it is not set, verification is skipped for local
development. Contact submissions are saved in Supabase and can be managed from
the Supabase table editor.

Authenticated routes use `Authorization: Bearer <access_token>`. Protect an
admin endpoint by adding `user: AuthUser = Depends(get_current_user)` to its
parameters. Portfolio read endpoints remain public for the website.

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
