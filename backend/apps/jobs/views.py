from rest_framework.views import APIView
from rest_framework import status
from django.db import connection
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from apps.jobs.selectors import (
    get_job_by_id,
    list_jobs,
    get_job_metrics,
    list_executions_for_job,
    get_dashboard_stats,
    get_workers_telemetry,
)
from apps.jobs.services import JobService
from apps.jobs.serializers import (
    JobSubmitRequestSerializer,
    JobSubmitResponseDataSerializer,
    JobListSerializer,
    JobDetailSerializer,
    JobMetricsSerializer,
    ExecutionSerializer,
)
from apps.common.pagination import StandardResultsSetPagination
from apps.common.utils import success_response


class JobListCreateAPIView(APIView):
    """
    Submit background jobs or list jobs with multi-field filtering and pagination.
    """
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        operation_id="list_jobs",
        summary="List and filter jobs",
        description=(
            "Retrieves a paginated list of background jobs. Supports filtering by status, "
            "task_type, priority, project_id, and free-text search."
        ),
        parameters=[
            OpenApiParameter("status", str, description="Filter by status (e.g. PENDING, QUEUED, COMPLETED)"),
            OpenApiParameter("task_type", str, description="Filter by task type identifier"),
            OpenApiParameter("priority", int, description="Filter by priority (1-10)"),
            OpenApiParameter("project_id", str, description="Filter by project UUID"),
            OpenApiParameter("search", str, description="Search across job ID and task type"),
            OpenApiParameter("page", int, description="Page number (default: 1)"),
            OpenApiParameter("page_size", int, description="Results per page (default: 20, max: 100)"),
        ],
        responses={200: JobListSerializer(many=True)},
    )
    def get(self, request):
        status_param = request.query_params.get("status")
        task_type_param = request.query_params.get("task_type")
        priority_param = request.query_params.get("priority")
        project_id_param = request.query_params.get("project_id")
        search_param = request.query_params.get("search")

        parsed_priority = None
        if priority_param:
            try:
                parsed_priority = int(priority_param)
            except ValueError:
                pass

        jobs_qs = list_jobs(
            project_id=project_id_param,
            status=status_param,
            task_type=task_type_param,
            priority=parsed_priority,
            search=search_param,
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(jobs_qs, request, view=self)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = JobListSerializer(jobs_qs, many=True)
        return success_response(
            data={"results": serializer.data, "count": jobs_qs.count()},
            message="Jobs retrieved successfully",
        )

    @extend_schema(
        operation_id="submit_job",
        summary="Submit a background job",
        description=(
            "Ingests and validates a new background job into PostgreSQL inside an atomic transaction.\n\n"
            "Notice: Job acceptance means the job was successfully stored with status PENDING/QUEUED. "
            "It does not imply immediate asynchronous worker execution in Phase 1."
        ),
        request=JobSubmitRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=JobSubmitResponseDataSerializer,
                description="Job submitted successfully",
            ),
            400: OpenApiResponse(description="Validation or payload error"),
            404: OpenApiResponse(description="Target project does not exist"),
        },
    )
    def post(self, request):
        serializer = JobSubmitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = JobService.submit_job(**serializer.validated_data)
        response_data = JobSubmitResponseDataSerializer(job).data

        return success_response(
            data=response_data,
            message="Job submitted successfully. Job stored in PostgreSQL; execution is scheduled for Phase 2.",
            status_code=status.HTTP_201_CREATED,
        )


class JobDetailAPIView(APIView):
    """
    Retrieve inspection details for a single job by UUID.
    Arbitrary updates (PUT/PATCH) are strictly prohibited.
    """

    @extend_schema(
        operation_id="retrieve_job",
        summary="Retrieve job details",
        description="Inspects complete parameters, payload, timestamps, and lifecycle metadata for a job.",
        responses={
            200: JobDetailSerializer,
            404: OpenApiResponse(description="Job not found"),
        },
    )
    def get(self, request, job_id):
        job = get_job_by_id(job_id)
        return success_response(
            data=JobDetailSerializer(job).data,
            message="Job details retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class JobMetricsAPIView(APIView):
    """
    Aggregated job metrics for dashboard overview.
    """

    @extend_schema(
        operation_id="job_metrics",
        summary="Get job counts by status",
        description="Retrieves live aggregate metrics across all lifecycle states for the dashboard.",
        parameters=[
            OpenApiParameter("project_id", str, description="Optional project UUID filter"),
        ],
        responses={200: JobMetricsSerializer},
    )
    def get(self, request):
        project_id = request.query_params.get("project_id")
        metrics = get_job_metrics(project_id=project_id)
        return success_response(
            data=metrics,
            message="Job metrics retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class JobExecutionListAPIView(APIView):
    """
    List all execution attempts and timing diagnostics for a specific job.
    """

    @extend_schema(
        operation_id="list_job_executions",
        summary="List execution history for a job",
        description="Retrieves the historical record of worker processing attempts, durations, and diagnostics.",
        responses={200: ExecutionSerializer(many=True)},
    )
    def get(self, request, job_id):
        executions = list_executions_for_job(job_id)
        serializer = ExecutionSerializer(executions, many=True)
        return success_response(
            data=serializer.data,
            message="Execution history retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class WorkerListAPIView(APIView):
    """
    Worker telemetry endpoint providing live information about connected Celery workers.
    """

    @extend_schema(
        operation_id="list_workers",
        summary="List active background workers",
        description="Inspects the Celery message broker and returns discovered worker nodes, concurrency, and active tasks.",
    )
    def get(self, request):
        workers = get_workers_telemetry()
        return success_response(
            data={"workers": workers, "count": len(workers)},
            message="Worker telemetry retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class DashboardStatsAPIView(APIView):
    """
    Comprehensive execution metrics and throughput stats for the Phase 2 dashboard.
    """

    @extend_schema(
        operation_id="dashboard_stats",
        summary="Get execution statistics",
        description="Aggregates execution throughput, average execution durations, and recent executions.",
        parameters=[
            OpenApiParameter("project_id", str, description="Optional project UUID filter"),
        ],
    )
    def get(self, request):
        project_id = request.query_params.get("project_id")
        stats = get_dashboard_stats(project_id=project_id)
        return success_response(
            data=stats,
            message="Dashboard execution statistics retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


class HealthCheckAPIView(APIView):
    """
    Multi-component health check distinguishing API, PostgreSQL, and Redis connectivity.
    """

    @extend_schema(
        operation_id="system_health",
        summary="System component health check",
        description="Verifies the operational status of the Django API, PostgreSQL database, and Redis message broker.",
    )
    def get(self, request):
        # 1. Database Health Check
        db_healthy = False
        db_error = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                db_healthy = row is not None and row[0] == 1
        except Exception as e:
            db_error = str(e)

        # 2. Redis Broker Health Check
        redis_healthy = False
        redis_error = None
        try:
            import redis
            broker_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
            r = redis.Redis.from_url(broker_url, socket_timeout=1.0)
            redis_healthy = bool(r.ping())
        except Exception as e:
            redis_error = str(e)

        overall_status = "healthy" if (db_healthy and redis_healthy) else "degraded"
        status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        health_data = {
            "status": overall_status,
            "api": "healthy",
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "engine": settings.DATABASES["default"]["ENGINE"],
                "name": settings.DATABASES["default"]["NAME"],
                "error": db_error,
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "broker_url": getattr(settings, "REDIS_URL", ""),
                "error": redis_error,
            },
            "worker_note": "Worker presence depends on active daemon processes. Check /api/v1/workers/ for live nodes.",
        }

        return success_response(
            data=health_data,
            message=f"System health check: {overall_status}",
            status_code=status_code,
        )


