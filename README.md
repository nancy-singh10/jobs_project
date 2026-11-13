# FlowOps — Distributed Background Job Processing & Orchestration Platform

> **Phase 1 Implementation: Job Submission & Management Foundation**

FlowOps solves the problem of blocking HTTP requests in web applications (e-commerce, fintech, EdTech) by offloading computationally heavy operations (invoices, reports, notifications, data sync) to an asynchronous background processing foundation.

Phase 1 provides an immediate job ingestion REST API, strict payload validation, ACID PostgreSQL storage, explicit lifecycle state tracking, and a modern React dashboard.

---

## ⚡ Quick Run Guide

### 1. Database Setup & Migrations
```bash
# Apply database migrations to PostgreSQL
python backend/manage.py migrate

# (Optional) Seed initial projects and jobs
python backend/manage.py seed_phase1
```

### 2. Start the Backend API Server
```bash
python backend/manage.py runserver 0.0.0.0:8000
```
- **Backend API Base:** [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)
- **Swagger Documentation:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **OpenAPI 3.0 Schema:** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### 3. Start the Frontend Dashboard (React + Vite)
```bash
cd frontend
npm run dev
```
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)

### 4. Run Automated Tests
```bash
pytest
```
*33/33 tests passing with 100% coverage.*

---

## 🏗️ Architecture & Technology Stack

- **Backend:** Python 3.11, Django 5.2, Django REST Framework 3.17
- **Database:** PostgreSQL 17 (`flowops_db`)
- **API Documentation:** drf-spectacular (OpenAPI 3.0 / Swagger UI)
- **Frontend:** React 19, Vite 8, Tailwind CSS, Axios, React Router, Lucide Icons
- **Testing:** Pytest, pytest-django

---

## 📋 Phase 1 Implementation Tracker (10/10)

- [x] Django and PostgreSQL configured with modular settings
- [x] Project model and CRUD REST APIs created
- [x] Job model, compound indexes, and PostgreSQL migrations completed
- [x] Job submission API working with immediate UUID and atomic transaction
- [x] Job listing, multi-field filtering, search, and pagination working
- [x] Job detail inspection page with lifecycle timeline working
- [x] Real-time metrics API powering dashboard overview cards
- [x] Swagger UI & OpenAPI 3.0 documentation available
- [x] 33 automated backend unit and integration tests passing
- [x] React developer dashboard and Django backend integrated end-to-end

---

## 📚 Complete Documentation Suite

- [`docs/01-problem-statement.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/01-problem-statement.md)
- [`docs/02-phase-1-requirements.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/02-phase-1-requirements.md)
- [`docs/03-architecture.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/03-architecture.md)
- [`docs/04-database-design.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/04-database-design.md)
- [`docs/05-api-documentation.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/05-api-documentation.md)
- [`docs/06-job-lifecycle.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/06-job-lifecycle.md)
- [`docs/07-frontend-design.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/07-frontend-design.md)
- [`docs/08-testing.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/08-testing.md)
- [`docs/09-setup-and-run.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/09-setup-and-run.md)
- [`docs/10-phase-1-limitations.md`](file:///c:/Users/NANCY_SINGH/Documents/BACKEND/django/new_projects/backend_project/docs/10-phase-1-limitations.md)

