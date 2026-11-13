import logging
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from apps.jobs.models import Job
from apps.jobs.choices import JobStatus
from apps.projects.selectors import get_project_by_id
from apps.common.exceptions import (
    InvalidStateTransitionError,
    ApplicationError,
)

logger = logging.getLogger(__name__)


def dispatch_job_task(job_id: str) -> bool:
    """
    Dispatches a job ID to the Celery broker (Redis).
    Invoked within transaction.on_commit() to ensure the database record is
    committed before worker consumers dequeue the task.

    Failure behavior:
      If Redis or the broker is unreachable, the job remains in PENDING state
      and the dispatch error is recorded for future reconciliation.
    """
    try:
        from apps.jobs.tasks import process_job
        process_job.delay(str(job_id))
        Job.objects.filter(id=job_id, status=JobStatus.PENDING).update(status=JobStatus.QUEUED)
        logger.info("Successfully dispatched job %s to Celery/Redis", job_id)
        return True
    except Exception as exc:
        logger.error("Failed to publish job %s to Redis broker: %s", job_id, exc)
        Job.objects.filter(id=job_id).update(
            error_message=f"Broker dispatch warning: {str(exc)}. Retained in PENDING state."
        )
        return False


class JobLifecycleService:
    """
    State machine service governing job lifecycle transitions.
    Defines allowed transitions and validates that states cannot jump arbitrarily.

    In Phase 1:
      - Only PENDING and QUEUED initial states are operational.
      - State transition validation ensures future Phase 2 worker engine compatibility.
      - Arbitrary client transitions (e.g. directly setting COMPLETED) are strictly blocked.
    """

    # Directed acyclic graph of valid status transitions
    VALID_TRANSITIONS = {
        JobStatus.PENDING: {JobStatus.QUEUED, JobStatus.CANCELLED},
        JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED},
        JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED},
        JobStatus.COMPLETED: set(),   # Terminal state
        JobStatus.FAILED: set(),      # Terminal state
        JobStatus.CANCELLED: set(),   # Terminal state
    }

    @classmethod
    def can_transition(cls, current_status: str, target_status: str) -> bool:
        """
        Returns True if transitioning from current_status to target_status is valid.
        """
        allowed = cls.VALID_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def validate_transition(cls, current_status: str, target_status: str) -> None:
        """
        Raises InvalidStateTransitionError if the state change is illegal.
        """
        if current_status == target_status:
            return

        if not cls.can_transition(current_status, target_status):
            allowed_states = [s.value for s in cls.VALID_TRANSITIONS.get(current_status, set())]
            raise InvalidStateTransitionError(
                message=f"Illegal state transition from '{current_status}' to '{target_status}'.",
                details={
                    "current_status": current_status,
                    "target_status": target_status,
                    "allowed_transitions": allowed_states,
                },
            )

    @classmethod
    def transition(
        cls,
        *,
        job: Job,
        target_status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Job:
        """
        Transitions a job to a target status with proper timestamp and audit tracking.
        Must be invoked inside an atomic transaction.
        """
        cls.validate_transition(job.status, target_status)

        with transaction.atomic():
            # Refresh from DB with lock to prevent race conditions
            locked_job = Job.objects.select_for_update().get(id=job.id)
            cls.validate_transition(locked_job.status, target_status)

            locked_job.status = target_status
            now = timezone.now()

            if target_status == JobStatus.RUNNING and not locked_job.started_at:
                locked_job.started_at = now
            elif target_status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
                if not locked_job.completed_at:
                    locked_job.completed_at = now

            if result is not None:
                locked_job.result = result

            if error_message is not None:
                locked_job.error_message = error_message

            locked_job.save()
            return locked_job


class JobService:
    """
    High-level business service for job submission and management.
    """

    @classmethod
    def submit_job(
        cls,
        *,
        project_id,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        status: str = JobStatus.PENDING,
        dispatch: bool = True,
    ) -> Job:
        """
        Validates project existence, ensures priority is within [1, 10],
        verifies submission state is either PENDING or QUEUED, and persists
        the job record in PostgreSQL within an atomic database transaction.

        In Phase 2, automatically registers a post-commit hook to dispatch
        the job ID to the Celery broker (Redis).

        Returns the newly created Job entity.
        """
        # Validate target project
        project = get_project_by_id(project_id)

        # Enforce valid priority
        if not (1 <= priority <= 10):
            raise ApplicationError(
                message="Priority must be an integer between 1 and 10.",
                code="INVALID_PRIORITY",
                details={"priority": priority},
            )

        # In Phase 1 & 2, submitted jobs enter either PENDING or QUEUED
        if status not in {JobStatus.PENDING, JobStatus.QUEUED}:
            raise ApplicationError(
                message=f"Initial submission status must be '{JobStatus.PENDING}' or '{JobStatus.QUEUED}'.",
                code="INVALID_INITIAL_STATUS",
                details={"status": status},
            )

        if not isinstance(payload, dict):
            raise ApplicationError(
                message="Job payload must be a valid JSON object.",
                code="INVALID_PAYLOAD",
                details={"payload": "Must be a JSON object (dictionary)."},
            )

        with transaction.atomic():
            job = Job.objects.create(
                project=project,
                task_type=task_type.strip(),
                payload=payload,
                status=status,
                priority=priority,
            )
            if dispatch:
                # Use transaction.on_commit to guarantee the job is committed to PostgreSQL
                # before Celery workers attempt to dequeue it from Redis
                transaction.on_commit(lambda: dispatch_job_task(str(job.id)))
            return job

