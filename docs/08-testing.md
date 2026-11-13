# FlowOps — Testing Strategy & Test Suite Results

## 1. Test Architecture

The testing suite utilizes **Pytest** and **pytest-django**, executing against the PostgreSQL database engine to ensure exact compatibility with production constraints, UUID generation, JSONField operations, and CheckConstraints.

Configured in `pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = tests.py test_*.py *_tests.py
pythonpath = . backend
addopts = -v --tb=short
```

---

## 2. Test Coverage Matrix (33 Automated Tests)

### Projects App (`test_projects.py` - 8 Tests)
- `test_create_project_success`: Valid project creation with standard 201 response.
- `test_create_project_duplicate_name`: Case-insensitive unique project name enforcement.
- `test_create_project_missing_name`: Rejection of missing/empty name with validation error.
- `test_list_projects`: Retrieval of project list with job count annotation.
- `test_retrieve_project_success`: Retrieval of single project by UUID.
- `test_retrieve_non_existent_project`: Returns standardized 404 envelope.
- `test_patch_project_success`: Partial update of description.
- `test_patch_project_unknown_field_rejected`: Strict serializer rejects unknown keys.

### Job Model (`test_models.py` - 2 Tests)
- `test_job_creation_default_values`: Verifies default `PENDING` state, priority 5, null result/error, and UUID.
- `test_job_priority_validation`: Enforces priority constraint between 1 and 10.

### Job Services & Lifecycle (`test_services.py` - 10 Tests)
- `test_submit_job_service_success`: Service creates job inside atomic transaction.
- `test_submit_job_service_queued_status`: Service allows initial `QUEUED` state.
- `test_submit_job_service_invalid_initial_status`: Rejects invalid initial submission states (e.g., `COMPLETED`).
- `test_submit_job_service_invalid_priority`: Rejects priority out of bounds.
- `test_submit_job_service_non_existent_project`: Raises `ResourceNotFoundError`.
- `test_lifecycle_allowed_transitions`: Happy path `PENDING` → `QUEUED` → `RUNNING` → `COMPLETED`.
- `test_lifecycle_failure_path`: Failure path `RUNNING` → `FAILED` with diagnostics.
- `test_lifecycle_cancellation_path`: Cancellation path `PENDING` → `CANCELLED`.
- `test_lifecycle_disallowed_transition_raises_error`: Blocks illegal jumps (`PENDING` → `COMPLETED`).
- `test_terminal_state_cannot_transition`: Prevents transitions out of terminal states.

### Job REST API Endpoints (`test_views.py` - 13 Tests)
- `test_submit_job_success`: Ingests job, returns 201, UUID, and ISO timestamp.
- `test_submit_job_missing_task_type`: Returns 400 for missing task type.
- `test_submit_job_invalid_priority_range`: Rejects priority > 10.
- `test_submit_job_priority_below_one`: Rejects priority < 1.
- `test_submit_job_invalid_payload_type`: Rejects string or non-object payloads.
- `test_submit_job_non_existent_project`: Rejects submission to non-existent project UUID.
- `test_submit_job_unknown_fields_rejected`: Strict serializer rejects rogue fields.
- `test_retrieve_job_success`: Fetches complete job details with Phase 1 note.
- `test_retrieve_non_existent_job`: Standard 404 response.
- `test_job_arbitrary_modification_prevented`: Rejects `PATCH`/`PUT` with 405 Method Not Allowed.
- `test_list_jobs_and_filtering`: Tests multi-field filtering by status, task type, priority, and project.
- `test_pagination`: Validates page size, total pages, and next/prev links.
- `test_metrics_endpoint`: Validates aggregated dashboard counts.

---

## 3. Running Backend Tests

```bash
# Run the complete test suite
pytest

# Run with verbose output and test names
pytest -v

# Run only job lifecycle service tests
pytest backend/apps/jobs/tests/test_services.py
```
Test Execution Result: **33 passed in ~2.2s**.

