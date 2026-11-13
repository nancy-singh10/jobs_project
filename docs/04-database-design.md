# FlowOps — Database Design & Schema Specification

## 1. Relational Database Overview

FlowOps relies on **PostgreSQL** as the single source of truth for all project tenants and background job records in Phase 1.

```
┌─────────────────────────────────┐
│        flowops_projects         │
├─────────────────────────────────┤
│ id (PK, UUID)                   │◄──────┐
│ name (VARCHAR 255, UNIQUE)      │       │
│ description (TEXT)              │       │
│ created_at (TIMESTAMPTZ)        │       │
│ updated_at (TIMESTAMPTZ)        │       │
└─────────────────────────────────┘       │ 1:N
                                          │ Relationship
┌─────────────────────────────────┐       │
│          flowops_jobs           │       │
├─────────────────────────────────┤       │
│ id (PK, UUID)                   │       │
│ project_id (FK -> Project)      ├───────┘
│ task_type (VARCHAR 255)         │
│ payload (JSONB)                 │
│ status (VARCHAR 20)             │
│ priority (SMALLINT 1-10)        │
│ result (JSONB, NULL)            │
│ error_message (TEXT, NULL)      │
│ created_at (TIMESTAMPTZ)        │
│ updated_at (TIMESTAMPTZ)        │
│ started_at (TIMESTAMPTZ, NULL)  │
│ completed_at (TIMESTAMPTZ, NULL)│
└─────────────────────────────────┘
```

---

## 2. Table Specifications

### A. `flowops_projects` (Project Entity)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `uuid_generate_v4()` | Unique tenant/project identifier |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | Unique project name |
| `description` | TEXT | DEFAULT `''` | Summary of application scope |
| `created_at` | TIMESTAMPTZ | NOT NULL, AUTO_NOW_ADD, INDEX | Timestamp of project registration |
| `updated_at` | TIMESTAMPTZ | NOT NULL, AUTO_NOW | Timestamp of last modification |

### B. `flowops_jobs` (Background Job Entity)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT `uuid_generate_v4()` | Public job identifier |
| `project_id` | UUID | FOREIGN KEY (`flowops_projects.id`), ON DELETE CASCADE | Associated project |
| `task_type` | VARCHAR(255) | NOT NULL, INDEX | Routing key (e.g., `invoice.generate`) |
| `payload` | JSONB | NOT NULL, DEFAULT `{}` | Immutable JSON task parameters |
| `status` | VARCHAR(20) | NOT NULL, INDEX, DEFAULT `'PENDING'` | Lifecycle state |
| `priority` | SMALLINT | NOT NULL, CHECK (`priority >= 1 AND priority <= 10`), DEFAULT 5 | Scheduling priority |
| `result` | JSONB | NULLABLE | Execution output (Phase 2) |
| `error_message` | TEXT | NULLABLE | Diagnostic failure info (Phase 2) |
| `created_at` | TIMESTAMPTZ | NOT NULL, AUTO_NOW_ADD, INDEX | Job submission timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, AUTO_NOW | Job update timestamp |
| `started_at` | TIMESTAMPTZ | NULLABLE | Worker start timestamp (Phase 2) |
| `completed_at` | TIMESTAMPTZ | NULLABLE | Terminal state timestamp (Phase 2) |

---

## 3. Database Indexes & Performance Design

To support low-latency querying and high-throughput job ingestion, the following compound and specialized indexes are defined:

1. **`job_proj_created_idx` on `(project_id, created_at DESC)`:**
   Accelerates tenant job history pagination and timeline sorting.
2. **`job_proj_status_idx` on `(project_id, status)`:**
   Accelerates dashboard status filters and per-project worker polling.
3. **`job_proj_task_idx` on `(project_id, task_type)`:**
   Allows instant filtering by task category for specific applications.
4. **`job_status_priority_idx` on `(status, priority DESC)`:**
   Directly prepares for Phase 2 priority dispatching (`SELECT FOR UPDATE SKIP LOCKED`).

---

## 4. UUID vs Sequential Identifiers

FlowOps standardizes on **UUIDv4** instead of sequential integer IDs for all public entities:
- **Security:** Sequential IDs allow enumeration attacks (`/jobs/1`, `/jobs/2`).
- **Distributed Generation:** UUIDs can be allocated across distributed nodes or client SDKs without central lock contention.
- **Multi-Tenant Privacy:** Clients cannot guess global platform job volumes based on sequential increments.
