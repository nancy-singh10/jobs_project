# FlowOps — Phase 1 Operational Boundaries & Known Limitations

## 1. Clear Architecture Boundaries

In accordance with Phase 1 design principles, this milestone establishes the **ingestion, validation, and persistence foundation**. It does not pretend to execute background tasks asynchronously.

---

## 2. Intentionally Postponed Features (Scheduled for Phase 2)

| Feature | Phase 1 Status | Phase 2 Target |
|---|---|---|
| **Asynchronous Execution** | NOT IMPLEMENTED (Stored in DB) | Distributed worker processes (Celery / RQ) |
| **In-Memory Message Broker** | NOT IMPLEMENTED | Redis Streams / Redis Queue |
| **Priority Job Dispatcher** | NOT IMPLEMENTED (Model & DB index ready) | Worker poll with `SELECT FOR UPDATE SKIP LOCKED` |
| **Retry Policy & Backoff** | NOT IMPLEMENTED | Exponential backoff with configurable max retries |
| **Dead Letter Queue (DLQ)** | NOT IMPLEMENTED | Poison pill isolation & failure inspection |
| **Multi-Job DAG Orchestration** | NOT IMPLEMENTED | Workflow graphs & dependent task chains |
| **Tenant API Keys & Token Auth** | Minimal developer open access | Scoped API tokens & Project-level RBAC |

---

## 3. Known Phase 1 Operational Characteristics

1. **Job Acceptance vs Execution:**
   - When the API returns HTTP 201 Created with `{ "status": "PENDING" }`, the job has been validated and persisted to PostgreSQL.
   - It will remain in `PENDING` (or `QUEUED`) state in Phase 1 until the Phase 2 worker engine is connected.
2. **State Transition Safeguards:**
   - Clients cannot arbitrarily call `PATCH /jobs/{id}/` to mark a job `COMPLETED`. The endpoint explicitly returns HTTP 405 Method Not Allowed to preserve lifecycle integrity.
3. **Payload Size Cap:**
   - Payloads are capped at 512 KB (`MAX_PAYLOAD_SIZE_BYTES`) to prevent denial-of-service through bloated JSON blobs in PostgreSQL.

