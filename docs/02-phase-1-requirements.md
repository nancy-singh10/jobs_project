# FlowOps — Phase 1 Requirements & Functional Specifications

## 1. Functional Scope

Phase 1 provides the complete ingestion and management layer for the FlowOps platform.

### A. Project Management
- **Project Registration:** Register external client applications or tenants that submit jobs.
- **Project Inspection:** Retrieve project metadata, description, creation timestamps, and live counts of associated jobs.
- **Project Updating:** Update name and description via partial update (`PATCH`).
- **Data Association:** All jobs must be bound to a valid, existing `Project` UUID.

### B. Job Ingestion (`POST /api/v1/jobs/`)
- Accept incoming job submission payloads containing:
  - `project_id`: Valid UUID referencing a registered project.
  - `task_type`: Non-empty routing string (e.g., `invoice.generate`, `email.send`).
  - `payload`: Valid JSON object (dictionary) containing task parameters (max 512 KB).
  - `priority`: Integer between 1 and 10 (defaults to 5).
  - `status`: Optional initial status (`PENDING` or `QUEUED`).
- Reject unexpected/unknown fields to prevent mass assignment vulnerabilities.
- Persist job in PostgreSQL inside an atomic database transaction.
- Return HTTP 201 Created with standard envelope and public UUID immediately.

### C. Job Retrieval & Inspection (`GET /api/v1/jobs/{job_id}/`)
- Lookup individual jobs by their public UUID.
- Return full parameter payload, timestamps, status, priority, and Phase 1 execution notice.
- Prohibit arbitrary updates (`PATCH`/`PUT`) to protect lifecycle integrity.

### D. Job Listing & Multi-Field Filtering (`GET /api/v1/jobs/`)
- Paginated listing with configurable page size (default 20, max 100).
- Multi-field filtering:
  - Filter by `status` (e.g., `PENDING`, `QUEUED`).
  - Filter by `task_type` (case-insensitive substring match).
  - Filter by `priority` (1–10).
  - Filter by `project_id` (UUID).
  - Free-text search on job UUID or task type.
- Consistent sorting by `created_at` descending.

### E. Metrics & Dashboard Overview (`GET /api/v1/jobs/metrics/`)
- Aggregated counts of:
  - Total Jobs
  - Pending Jobs
  - Queued Jobs
  - Running Jobs (0 in Phase 1)
  - Completed Jobs (0 in Phase 1)
  - Failed Jobs (0 in Phase 1)
  - Cancelled Jobs

### F. Developer Dashboard (React + Vite + Tailwind CSS)
- Modern SaaS interface with dark/zinc developer aesthetics.
- Real-time API-driven Overview cards.
- Interactive Job Submission form with JSON validation and preset task types.
- Searchable & filterable Jobs table.
- Detailed Job inspection modal/page with lifecycle timeline.
- Projects management screen with project creation and editing.
