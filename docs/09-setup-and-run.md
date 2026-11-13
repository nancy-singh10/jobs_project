# FlowOps — Setup & Execution Guide (Phase 1)

This guide provides step-by-step instructions to configure, run, and test FlowOps Phase 1.

---

## 1. Prerequisites

- **Python:** 3.11+
- **Node.js:** 18+ and npm
- **Database:** PostgreSQL 14+ (Running on `localhost:5432`)

---

## 2. Environment Configuration

1. Verify or create your `.env` file in the project root:
```ini
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
SECRET_KEY=flowops-insecure-dev-key-change-in-production-f38b29f9c0174e
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (PostgreSQL 17)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=flowops_db
DB_USER=postgres
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Payload Limit (bytes, 512 KB)
MAX_PAYLOAD_SIZE_BYTES=524288
```

---

## 3. Database Initialization & Seeding

```bash
# 1. Apply database migrations
python backend/manage.py migrate

# 2. (Optional) Seed realistic sample projects and Phase 1 jobs
python backend/manage.py seed_phase1
```

---

## 4. Running the Application

You need two terminal windows (one for the Django Backend, one for the React Frontend):

### Terminal 1: Start Django Backend API Server
```bash
python backend/manage.py runserver 0.0.0.0:8000
```
- **Backend API Base:** `http://127.0.0.1:8000/api/v1/`
- **Interactive Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **OpenAPI Schema:** `http://127.0.0.1:8000/api/schema/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

### Terminal 2: Start React Developer Dashboard (Vite)
```bash
cd frontend
npm run dev
```
- **Frontend Dashboard:** `http://localhost:5173`

---

## 5. Running Automated Backend Tests

```bash
# Run pytest from the project root
pytest
```
Expected output:
```
======================== 33 passed, 1 warning in 2.18s ========================
```

