# KarigarConnect Backend

A small FastAPI REST API foundation for the KarigarConnect Flutter application.

## Setup

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

Copy `.env.example` to `.env` when you need to customize the database or CORS origins. The default development database is `karigar_connect.db` in the backend directory.

## Run

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. Health check: `GET /health`.

## API endpoints

All resource endpoints use the `/api/v1` prefix:

- `POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` for `/users`
- `POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` for `/categories`
- `POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` for `/products`
- `POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` for `/enquiries`

There is no authentication, payment processing, or external AI integration yet.

## Test

```powershell
pytest
```

## Later integration work

Authentication and authorization, Flutter API client wiring, image upload/storage, search and discovery, AI-assisted cataloguing, notifications, payments, and production database migrations remain future work. OAuth, M2/M3/M5, and external AI services are intentionally not connected.
