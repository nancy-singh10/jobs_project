# FlowOps — Frontend Design & Component Architecture

## 1. Frontend Technology Stack

- **Framework:** React 19 + Vite 8
- **Styling:** Tailwind CSS (Dark Developer aesthetic: `#090a0f` background, indigo accent `#6366f1`)
- **HTTP Client:** Axios with response interceptors and standardized error unpacking
- **Routing:** React Router v7 (`BrowserRouter`, `Routes`, `Route`)
- **Icons:** Lucide React

---

## 2. Screen Hierarchy & Capabilities

### A. Dashboard (`/`)
- **Overview Cards:** Real-time query to `GET /api/v1/jobs/metrics/` showing Total Jobs, Pending, Queued, Completed, and Failed.
- **Recent Jobs Table:** 5 most recent database records with status badges, priority tags, and copyable UUIDs.
- **Projects Quick Glance:** List of tenant projects with associated job counts and direct filtering links.

### B. Jobs Page (`/jobs`)
- **Filter Bar:** Real-time search by Job ID or Task Type; dropdowns for Status, Project, and Priority.
- **Jobs Table:** Full paginated records with truncated UUID copy buttons, timestamps, and "Inspect" button.
- **Pagination Controls:** Shows page numbers, item counts, and Prev/Next buttons.

### C. Job Details Page (`/jobs/:jobId`)
- **Job Header:** Full UUID with copy button, StatusBadge, PriorityBadge.
- **Phase 1 Execution Notice:** Clear callout that the job is stored in PostgreSQL and worker execution is Phase 2.
- **Lifecycle Timeline:** Interactive 4-step state machine (`PENDING` → `QUEUED` → `RUNNING` → `COMPLETED`).
- **Payload Viewer:** Formatted JSON viewer with copy-to-clipboard functionality.
- **Metadata Card:** Project association, creation time, update time, and database target.

### D. Projects Page (`/projects`)
- **Projects Grid:** Cards displaying project name, description, creation date, and total job count.
- **Create Project Modal:** Ingests new tenant applications via `POST /api/v1/projects/`.
- **Edit Project Modal:** Updates existing projects via `PATCH /api/v1/projects/{id}/`.

### E. System Settings (`/settings`)
- **Storage Engine:** PostgreSQL 17 connection, host, port, database details.
- **API Documentation:** Direct links to Swagger UI and OpenAPI schema.
- **Phase 1 Checklist:** 10/10 completed verification checklist.
- **Phase 2 Roadmap:** Details on Redis broker, distributed workers, and DLQ retries.

