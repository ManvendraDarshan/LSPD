# Local Service Provider Directory (LSPD)

LSPD is a full-stack, location-aware directory for finding reliable local service providers in Madhya Pradesh, India. It supports customers, service providers, and super admins with JWT authentication, role-based authorization, provider discovery, reviews, verification workflows, and a responsive React UI with Leaflet/OpenStreetMap.

## Stack

- Frontend: React, Vite, Tailwind CSS, React Router, Axios, React Hot Toast, Leaflet
- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic, JWT, passlib/bcrypt
- Database: PostgreSQL with PostGIS geography points and spatial indexes
- Tooling: Docker Compose, pytest, Vitest

## Features

- Customer registration/login, dashboard, provider search, provider details, review submission
- Provider onboarding, profile creation, location coordinates, dashboard, verification status
- Super admin dashboard, provider approval/rejection, badge revoke, categories, customers, review moderation
- Location-aware provider search with city/category/rating/radius/sort filters
- Private verification document upload route restricted to provider owner or admin
- Seed data for Satna, Rewa, Bhopal, Indore, Jabalpur, and Gwalior

## Demo Credentials

All seeded demo accounts use password `DemoPass@123`.

- Customer: `customer@example.com`
- Provider: `provider@example.com`
- Admin: `admin@example.com`

Do not use these credentials in production.

## Requirements

Choose one setup method:

- Docker Desktop with Docker Compose (recommended on Windows), or
- Python 3.12+, Node.js 20+, and PostgreSQL 16 with the PostGIS extension.

Git is optional if you already have the project files.

## Run With Docker (Recommended)

Open PowerShell in the project folder:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace `JWT_SECRET_KEY` with a long random value. For a quick local-only value, use:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the printed value into `.env`. Then build and start all services:

```powershell
docker compose up --build
```

The first startup creates the PostgreSQL database, enables the schema through Alembic migrations, and installs the demo data. Keep this terminal open to see service logs.

Open these URLs:

- Application: <http://localhost:5173>
- API health check: <http://localhost:8000/api/health>
- Database health check: <http://localhost:8000/api/health/db>
- Swagger API documentation: <http://localhost:8000/api/docs>

To stop the services, press `Ctrl+C`, then run:

```powershell
docker compose down
```

To remove the database and start from an empty database, use this only when you are willing to lose local data:

```powershell
docker compose down -v
docker compose up --build
```

## Run Without Docker

Install PostgreSQL with PostGIS, create a database named `lspd`, and make sure the database is running. Then open PowerShell in the project folder:

```powershell
Copy-Item .env.example .env
```

Update `.env` if your local PostgreSQL username, password, host, or port differs from the defaults. Create and activate the backend environment:

```powershell
Set-Location backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run migrations and seed data from the `backend` folder:

```powershell
alembic upgrade head
python ..\database\seed\seed.py
uvicorn app.main:app --reload
```

In a second PowerShell window, start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

If PowerShell blocks script activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that window and activate the environment again. The frontend uses `VITE_API_URL` from `frontend/.env` when present; otherwise it defaults to `http://localhost:8000/api`.

## Use The Application

1. Open <http://localhost:5173> and choose **Log in** or **Register**.
2. Use the seeded customer account to search providers, filter by city/category/rating, open provider details, and submit a review.
3. Use the seeded provider account to open the provider dashboard and manage the provider profile.
4. Use the seeded admin account to review providers, approve or reject verification, manage categories, and moderate reviews.
5. Provider registration is available from the public navigation at `/provider/register`; a provider account must be logged in before creating a provider profile.

All seeded accounts use password `DemoPass@123`:

| Role | Email |
| --- | --- |
| Customer | `customer@example.com` |
| Provider | `provider@example.com` |
| Admin | `admin@example.com` |

These credentials are for local demonstration only. Change them before deploying anywhere public.

## Environment Variables

See `.env.example`.

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL, for example `postgresql+psycopg://lspd:lspd@localhost:5432/lspd`
- `JWT_SECRET_KEY`: long random signing secret
- `FRONTEND_URL`: allowed CORS frontend origin
- `UPLOAD_DIR`: private upload root
- `MAX_UPLOAD_MB`: upload size limit
- `MAP_PROVIDER` / `MAP_API_KEY`: reserved for future map providers; OpenStreetMap works without a key

## Important API Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/health/db`
- `GET /api/providers`
- `GET /api/providers/{id}`
- `POST /api/providers`
- `PUT /api/providers/{id}`
- `GET /api/search/providers`
- `GET /api/search/nearby`
- `GET /api/categories`
- `POST /api/providers/{id}/reviews`
- `GET /api/providers/{id}/reviews`
- `GET /api/admin/dashboard`
- `GET /api/admin/providers`
- `PUT /api/admin/providers/{id}/approve`
- `PUT /api/admin/providers/{id}/reject`
- `PUT /api/admin/providers/{id}/revoke-verification`
- `GET /api/admin/reviews`
- `PUT /api/admin/reviews/{id}`

## Testing

Run these checks from the project folder. Backend tests use the configured database URL and should be run with PostgreSQL/PostGIS available.

```powershell
Set-Location backend
pytest
```

Frontend tests and the production build:

```powershell
Set-Location frontend
npm test
npm run build
```

## Architecture Notes

- Provider coordinates are stored as latitude/longitude for UI display and as a PostGIS `geography(Point, 4326)` for radius search.
- Verification documents are not exposed by public endpoints; admin document reads return metadata only.
- Categories are database-driven and deactivated rather than hard-deleted, preserving provider relationships.
- Search ranking combines verification, rating, review count, and distance-aware sorting options.
- Future booking, payments, notifications, mobile apps, multilingual content, and analytics can be added without changing the core auth/provider/category/review model.

## Troubleshooting

- `docker` is not recognized: install and start Docker Desktop, then reopen PowerShell.
- The frontend cannot reach the API: confirm `http://localhost:8000/api/health` opens successfully and check `VITE_API_URL`.
- Provider registration shows a database error: PostgreSQL may be using a different password for the `lspd` user than the value in `.env`. Sign in to PostgreSQL as an administrator and run `ALTER USER lspd WITH PASSWORD 'lspd';`, then confirm `.env` contains `DATABASE_URL=postgresql+psycopg://lspd:lspd@localhost:5432/lspd`. Run `alembic upgrade head` and `python ..\database\seed\seed.py` from `backend`, then refresh the registration page.
- Docker backend exits while seeding: rebuild after pulling the latest files with `docker compose build --no-cache backend`.
- If migrations fail with PostGIS errors, confirm the database user can run `CREATE EXTENSION postgis`.
- If maps do not load, check browser network access to OpenStreetMap tile servers.
- If CORS blocks requests, set `FRONTEND_URL` to the exact Vite origin.
- If document uploads fail, check `UPLOAD_DIR` permissions and file type/size.
- If a seeded account cannot log in after changing the database, run the seed command again or remove the Docker volume and recreate the services.

For a quick service check, open <http://localhost:8000/api/health>. A working API returns:

```json
{"success":true,"message":"LSPD API is healthy"}
```
