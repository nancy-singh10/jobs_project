# FlowOps — API Documentation & Specification (Phase 1)

Base API Path: `/api/v1/`

Interactive Documentation:
- **Swagger UI:** `http://localhost:8000/api/docs/` or `http://localhost:8000/api/v1/docs/`
- **Redoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

---

## 1. Projects API

### A. List Projects
- **Endpoint:** `GET /api/v1/projects/`
- **Description:** Returns all registered tenant applications with annotated job counts.
- **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Projects retrieved successfully",
  "data": [
    {
      "id": "e4a7702a-9cb8-48b4-8e14-d886915fb7e9",
      "name": "E-Commerce Platform",
      "description": "High-volume retail checkout and invoice processing.",
      "jobs_count": 12,
      "created_at": "2026-11-12T17:00:00Z",
      "updated_at": "2026-11-12T17:00:00Z"
    }
  ]
}
```

### B. Create Project
- **Endpoint:** `POST /api/v1/projects/`
- **Request Body:**
```json
{
  "name": "Fintech Settlement Hub",
  "description": "Ledger reconciliation and batch settlement engine."
}
```
- **Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Project created successfully",
  "data": {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "name": "Fintech Settlement Hub",
    "description": "Ledger reconciliation and batch settlement engine.",
    "jobs_count": 0,
    "created_at": "2026-11-12T17:15:00Z",
    "updated_at": "2026-11-12T17:15:00Z"
  }
}
```

### C. Retrieve Project
- **Endpoint:** `GET /api/v1/projects/{project_id}/`
- **Success Response (200 OK):** Project detail object.
- **Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Project with ID '...' does not exist.",
    "details": {}
  }
}
```

### D. Update Project
- **Endpoint:** `PATCH /api/v1/projects/{project_id}/`
- **Request Body:** Partial update fields (`name`, `description`).
- **Success Response (200 OK):** Updated project object.

---

## 2. Jobs API

### A. Submit Job
- **Endpoint:** `POST /api/v1/jobs/`
- **Description:** Validates task parameters, generates a public UUID, and persists the job in PostgreSQL.
- **Request Body:**
```json
{
  "project_id": "e4a7702a-9cb8-48b4-8e14-d886915fb7e9",
  "task_type": "invoice.generate",
  "payload": {
    "invoice_id": 10428,
    "customer_email": "customer@example.com",
    "total_usd": 249.99
  },
  "priority": 7,
  "status": "PENDING"
}
```
- **Validation Rules:**
  - `project_id`: Must reference an existing project.
  - `task_type`: Mandatory non-empty string.
  - `payload`: Must be a valid JSON dictionary (max 512 KB).
  - `priority`: Optional integer from 1 to 10 (default: 5).
  - `status`: Optional initial status (`PENDING` or `QUEUED`).
  - Extraneous fields are strictly rejected.
- **Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Job submitted successfully. Job stored in PostgreSQL; execution is scheduled for Phase 2.",
  "data": {
    "id": "7b82427a-514d-487e-9764-87cf7a4ee709",
    "task_type": "invoice.generate",
    "status": "PENDING",
    "priority": 7,
    "created_at": "2026-11-12T17:20:00Z"
  }
}
```

### B. List Jobs (Filtering & Pagination)
- **Endpoint:** `GET /api/v1/jobs/`
- **Query Parameters:**
  - `status`: Filter by status (`PENDING`, `QUEUED`, etc.).
  - `task_type`: Substring match on task type.
  - `priority`: Filter by priority integer (1–10).
  - `project_id`: Filter by project UUID.
  - `search`: Search across UUID and task type.
  - `page`: Page number (default: 1).
  - `page_size`: Results per page (default: 20, max: 100).
- **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Resource list retrieved successfully",
  "data": {
    "count": 45,
    "page": 1,
    "page_size": 20,
    "total_pages": 3,
    "next": "http://localhost:8000/api/v1/jobs/?page=2",
    "previous": null,
    "results": [
      {
        "id": "7b82427a-514d-487e-9764-87cf7a4ee709",
        "project_id": "e4a7702a-9cb8-48b4-8e14-d886915fb7e9",
        "project_name": "E-Commerce Platform",
        "task_type": "invoice.generate",
        "status": "PENDING",
        "priority": 7,
        "created_at": "2026-11-12T17:20:00Z"
      }
    ]
  }
}
```

### C. Retrieve Job Details
- **Endpoint:** `GET /api/v1/jobs/{job_id}/`
- **Description:** Retrieve full parameters, payload, timestamps, and execution notes.
- **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Job details retrieved successfully",
  "data": {
    "id": "7b82427a-514d-487e-9764-87cf7a4ee709",
    "project_id": "e4a7702a-9cb8-48b4-8e14-d886915fb7e9",
    "project_name": "E-Commerce Platform",
    "task_type": "invoice.generate",
    "payload": {
      "invoice_id": 10428,
      "customer_email": "customer@example.com"
    },
    "status": "PENDING",
    "priority": 7,
    "result": null,
    "error_message": null,
    "created_at": "2026-11-12T17:20:00Z",
    "updated_at": "2026-11-12T17:20:00Z",
    "started_at": null,
    "completed_at": null,
    "phase_1_status_note": "Job persisted in PostgreSQL. Distributed worker execution is scheduled for Phase 2."
  }
}
```

### D. Job Metrics
- **Endpoint:** `GET /api/v1/jobs/metrics/?project_id={optional_uuid}`
- **Description:** Live aggregates powering the dashboard overview cards.
- **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Job metrics retrieved successfully",
  "data": {
    "total_jobs": 128,
    "pending_jobs": 110,
    "queued_jobs": 18,
    "running_jobs": 0,
    "completed_jobs": 0,
    "failed_jobs": 0,
    "cancelled_jobs": 0
  }
}
```

