from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, Count, Avg, Q
from apps.jobs.models import Job, Execution
from apps.jobs.choices import JobStatus, ExecutionStatus
from apps.common.exceptions import ResourceNotFoundError


def get_job_by_id(job_id) -> Job:
    """
    Retrieves a single Job by UUID with related project and executions prefetched,
    or raises ResourceNotFoundError.
    """
    try:
        return Job.objects.select_related("project").prefetch_related("executions").get(id=job_id)
    except (Job.DoesNotExist, ValueError):
        raise ResourceNotFoundError(f"Job with ID '{job_id}' does not exist.")


def list_executions_for_job(job_id: str) -> QuerySet[Execution]:
    """
    Retrieves all execution records for a specific job, ordered by attempt.
    """
    # Ensure job exists
    get_job_by_id(job_id)
    return Execution.objects.filter(job_id=job_id).order_by("attempt_number")


def get_dashboard_stats(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Detailed execution and throughput metrics for the dashboard stats endpoint.
    """
    job_qs = Job.objects.all()
    exec_qs = Execution.objects.all()

    if project_id:
        job_qs = job_qs.filter(project_id=project_id)
        exec_qs = exec_qs.filter(job__project_id=project_id)

    job_aggregates = job_qs.aggregate(
        total_jobs=Count("id"),
        pending_jobs=Count("id", filter=Q(status=JobStatus.PENDING)),
        queued_jobs=Count("id", filter=Q(status=JobStatus.QUEUED)),
        running_jobs=Count("id", filter=Q(status=JobStatus.RUNNING)),
        completed_jobs=Count("id", filter=Q(status=JobStatus.COMPLETED)),
        failed_jobs=Count("id", filter=Q(status=JobStatus.FAILED)),
    )

    exec_aggregates = exec_qs.aggregate(
        total_executions=Count("id"),
        avg_duration_ms=Avg("duration_ms", filter=Q(status=ExecutionStatus.COMPLETED)),
    )

    recent_executions = (
        exec_qs.select_related("job", "job__project")
        .order_by("-started_at")[:10]
    )

    return {
        "total_jobs": job_aggregates["total_jobs"] or 0,
        "running_jobs": job_aggregates["running_jobs"] or 0,
        "completed_jobs": job_aggregates["completed_jobs"] or 0,
        "failed_jobs": job_aggregates["failed_jobs"] or 0,
        "pending_jobs": job_aggregates["pending_jobs"] or 0,
        "queued_jobs": job_aggregates["queued_jobs"] or 0,
        "total_executions": exec_aggregates["total_executions"] or 0,
        "avg_duration_ms": round(exec_aggregates["avg_duration_ms"] or 0, 1),
        "recent_executions": [
            {
                "id": str(e.id),
                "job_id": str(e.job_id),
                "task_type": e.job.task_type,
                "project_name": e.job.project.name,
                "worker_name": e.worker_name,
                "status": e.status,
                "duration_ms": e.duration_ms,
                "started_at": e.started_at,
                "ended_at": e.ended_at,
            }
            for e in recent_executions
        ],
    }


def get_workers_telemetry() -> List[Dict[str, Any]]:
    """
    Queries Celery broker inspect API for live worker telemetry.
    Returns worker names, active task count, registered tasks, and status.
    """
    workers = []
    try:
        from config.celery import app as celery_app
        inspector = celery_app.control.inspect(timeout=1.0)
        
        ping_res = inspector.ping() or {}
        active_res = inspector.active() or {}
        registered_res = inspector.registered() or {}
        stats_res = inspector.stats() or {}

        all_hostnames = set(ping_res.keys()) | set(active_res.keys()) | set(stats_res.keys())

        for host in sorted(all_hostnames):
            active_tasks = active_res.get(host, [])
            concurrency = stats_res.get(host, {}).get("pool", {}).get("max-concurrency", 1)
            reg_tasks = registered_res.get(host, [])

            workers.append({
                "name": host,
                "status": "Online" if host in ping_res else "Offline",
                "active_tasks_count": len(active_tasks),
                "concurrency": concurrency,
                "registered_tasks": reg_tasks,
            })
    except Exception:
        # If Celery inspector is unavailable or broker is not reachable
        pass

    return workers



def list_jobs(
    *,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    priority: Optional[int] = None,
    search: Optional[str] = None,
) -> QuerySet[Job]:
    """
    Returns a filtered QuerySet of Jobs, selecting related projects.
    Supports multi-field filtering and searching.
    """
    queryset = Job.objects.select_related("project").order_by("-created_at")

    if project_id:
        queryset = queryset.filter(project_id=project_id)

    if status:
        queryset = queryset.filter(status=status.upper())

    if task_type:
        queryset = queryset.filter(task_type__icontains=task_type.strip())

    if priority is not None:
        queryset = queryset.filter(priority=priority)

    if search:
        search_term = search.strip()
        # If it looks like a UUID or substring
        queryset = queryset.filter(
            Q(id__icontains=search_term) | Q(task_type__icontains=search_term)
        )

    return queryset


def get_job_metrics(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates aggregated job counts across lifecycle states.
    Directly powers the FlowOps dashboard overview metrics.
    """
    qs = Job.objects.all()
    if project_id:
        qs = qs.filter(project_id=project_id)

    aggregates = qs.aggregate(
        total_jobs=Count("id"),
        pending_jobs=Count("id", filter=Q(status=JobStatus.PENDING)),
        queued_jobs=Count("id", filter=Q(status=JobStatus.QUEUED)),
        running_jobs=Count("id", filter=Q(status=JobStatus.RUNNING)),
        completed_jobs=Count("id", filter=Q(status=JobStatus.COMPLETED)),
        failed_jobs=Count("id", filter=Q(status=JobStatus.FAILED)),
        cancelled_jobs=Count("id", filter=Q(status=JobStatus.CANCELLED)),
    )

    return {
        "total_jobs": aggregates["total_jobs"] or 0,
        "pending_jobs": aggregates["pending_jobs"] or 0,
        "queued_jobs": aggregates["queued_jobs"] or 0,
        "running_jobs": aggregates["running_jobs"] or 0,
        "completed_jobs": aggregates["completed_jobs"] or 0,
        "failed_jobs": aggregates["failed_jobs"] or 0,
        "cancelled_jobs": aggregates["cancelled_jobs"] or 0,
    }

