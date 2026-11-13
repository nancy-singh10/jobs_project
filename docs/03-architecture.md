# FlowOps — System Architecture & Modular Design

## 1. Architectural Philosophy

FlowOps is built with a service-oriented architectural design separating database concerns, business domain logic, and HTTP presentation. This prevents the common anti-pattern of burying business logic in Django views, serializers, or model signals.

```
                    ┌────────────────────────────┐
                    │    HTTP Client Request     │
                    │  (REST API / React Client) │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │    Presentation Layer      │
                    │   (DRF Views & Routers)    │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │     Validation Layer       │
                    │   (Serializers & DTOs)     │
                    └─────────────┬──────────────┘
                                  │
                        ┌─────────┴─────────┐
                        ▼                   ▼
            ┌───────────────────────┐ ┌───────────────────────┐
            │     Service Layer     │ │    Selector Layer     │
            │ (Mutations & Atomic   │ │ (Read-only Queries &  │
            │    Transactions)      │ │     Aggregations)     │
            └───────────┬───────────┘ └───────────┬───────────┘
                        │                         │
                        ▼                         ▼
            ┌─────────────────────────────────────────────────┐
            │             Database Entities & ORM             │
            │           (PostgreSQL Models & Indexes)         │
            └─────────────────────────────────────────────────┘
```

---

## 2. Directory & App Structure

```
backend/
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py           # Shared settings, apps, drf-spectacular, cors
│   │   ├── development.py    # Dev settings, relaxed CORS, debug logging
│   │   └── production.py     # Hardened security headers, disabled debug
│   ├── urls.py               # Root API routing & Swagger / Redoc endpoints
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── common/               # Cross-cutting utilities & handlers
│   │   ├── exceptions.py     # Unified envelope exception handler
│   │   ├── pagination.py     # StandardResultsSetPagination (page_size, count, total_pages)
│   │   ├── permissions.py    # Base developer & project-scoped permissions
│   │   ├── utils.py          # Success response envelope helper
│   │   └── management/       # DB seeding commands
│   ├── projects/             # Tenant / Project management
│   │   ├── models.py         # Project entity (UUID primary key)
│   │   ├── serializers.py    # Strict serializers with unknown field rejection
│   │   ├── views.py          # Project list/create and detail views
│   │   ├── urls.py
│   │   ├── services.py       # Atomic creation & partial updating
│   │   ├── selectors.py      # Project listing with job count annotations
│   │   └── tests/
│   └── jobs/                 # Core Job Ingestion & Management
│       ├── models.py         # Job entity, compound indexes & priority constraints
│       ├── choices.py        # JobStatus choices
│       ├── serializers.py    # Ingestion validator, detail schema, metrics schema
│       ├── views.py          # Job submission, listing, inspection, metrics
│       ├── urls.py
│       ├── services.py       # Atomic job submission & JobLifecycleService
│       ├── selectors.py      # Multi-field query filtering & metrics aggregation
│       ├── permissions.py    # Strict mutation protection
│       └── tests/
└── manage.py
```

---

## 3. Layer Responsibilities

### Models (`models.py`)
- Define relational schema, data types, constraints, and database indexes.
- Do not contain HTTP or transaction orchestration logic.

### Serializers (`serializers.py`)
- Parse and validate input data types.
- Reject unknown or extra fields to prevent mass assignment vulnerabilities.
- Format outgoing JSON representations with ISO-8601 timestamps and camel/snake conventions.

### Services (`services.py`)
- Coordinate business mutations (writes, updates, deletions).
- Wrap operations within `django.db.transaction.atomic()` to ensure ACID consistency.
- Enforce domain invariant rules (e.g., job priority bounds, legal lifecycle state transitions).

### Selectors (`selectors.py`)
- Pure read queries returning QuerySets or serialized dictionaries.
- Isolate query optimizations (`select_related`, `annotate`, complex filters) from views.

### Views (`views.py`)
- Handle incoming HTTP requests, status codes, query parameter parsing, and call services/selectors.
- Decorated with `drf-spectacular` OpenAPI schema documentation.

---

## 4. Response Envelope Protocol

To provide predictability for API clients and frontend SDKs, all endpoints conform to an explicit envelope format:

### Standard Success Envelope
```json
{
  "success": true,
  "message": "Human readable status message",
  "data": { ... }
}
```

### Standard Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable summary",
    "details": {
      "field_name": ["Specific validation error"]
    }
  }
}
```
Stack traces and internal exception details are caught and suppressed in `apps.common.exceptions.custom_exception_handler`.
