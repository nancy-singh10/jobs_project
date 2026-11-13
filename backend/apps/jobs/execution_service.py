"""
Job Execution Service for FlowOps Phase 2.
Orchestrates worker-side claiming, state transition, execution timing,
handler dispatch, and durable PostgreSQL persistence.
"""
import logging
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from apps.jobs.models import Job, Execution
from apps.jobs.choices import JobStatus, ExecutionStatus
from apps.jobs.handlers import get_task_handler, TaskExecutionError
from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)


class JobExecutionService:
    """
    Dedicated worker execution service.
    Follows a two-phase transactional model:
      Phase A: Short transaction claiming the job and creating the RUNNING execution record.
      Execution: External task handler runs OUTSIDE database locks.
      Phase B: Short transaction recording the terminal state, timestamps, and output/error.
    """

    @classmethod
    def execute_job(cls, *, job_id: str, worker_name: str = "worker-default") -> Dict[str, Any]:
        """
        Executes a background job by ID.
        Returns a summary dictionary of the execution result or raises an exception.
        """
        start_time = timezone.now()

        # Step 1: Pre-flight state check
        try:
            job = Job.objects.get(id=job_id)
        except (Job.DoesNotExist, ValueError):
            logger.error("Job %s does not exist; aborting execution.", job_id)
            return {"success": False, "error": f"Job {job_id} not found"}

        # Prevent duplicate execution of finished or cancelled jobs
        if job.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
            logger.warning(
                "Job %s is already in terminal state '%s'; skipping execution.",
                job_id,
                job.status,
            )
            return {
                "success": False,
                "message": f"Job is already in terminal state '{job.status}'",
                "status": job.status,
            }

        # Step 2: Phase A Transaction (Claiming the job)
        execution_id = None
        attempt_number = 1
        with transaction.atomic():
            locked_job = Job.objects.select_for_update().get(id=job_id)

            # Re-check state inside row lock
            if locked_job.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
                logger.warning("Job %s claimed by another worker; skipping.", job_id)
                return {"success": False, "message": "Job already terminal"}

            attempt_number = locked_job.executions.count() + 1
            locked_job.status = JobStatus.RUNNING
            if not locked_job.started_at:
                locked_job.started_at = start_time
            locked_job.save(update_fields=["status", "started_at", "updated_at"])

            execution = Execution.objects.create(
                job=locked_job,
                attempt_number=attempt_number,
                worker_name=worker_name,
                status=ExecutionStatus.RUNNING,
                started_at=start_time,
            )
            execution_id = execution.id

        logger.info(
            "Worker '%s' claimed job '%s' [Attempt #%d] (Execution: %s)",
            worker_name,
            job_id,
            attempt_number,
            execution_id,
        )

        # Step 3: Run task handler OUTSIDE database transaction
        handler_error: Optional[str] = None
        handler_result: Optional[Dict[str, Any]] = None

        try:
            handler = get_task_handler(job.task_type)
            handler_result = handler(job.payload)
        except Exception as exc:
            handler_error = str(exc)
            logger.exception(
                "Job '%s' execution failed on worker '%s': %s",
                job_id,
                worker_name,
                handler_error,
            )

        end_time = timezone.now()
        duration_ms = max(1, int((end_time - start_time).total_seconds() * 1000))

        # Step 4: Phase B Transaction (Persisting terminal state and output)
        with transaction.atomic():
            target_job = Job.objects.select_for_update().get(id=job_id)
            target_execution = Execution.objects.select_for_update().get(id=execution_id)

            target_execution.ended_at = end_time
            target_execution.duration_ms = duration_ms

            if handler_error is not None:
                target_execution.status = ExecutionStatus.FAILED
                target_execution.error_message = handler_error
                target_job.status = JobStatus.FAILED
                target_job.error_message = handler_error
            else:
                target_execution.status = ExecutionStatus.COMPLETED
                target_execution.result = handler_result
                target_job.status = JobStatus.COMPLETED
                target_job.result = handler_result

            target_job.completed_at = end_time
            target_execution.save()
            target_job.save()

        return {
            "success": handler_error is None,
            "job_id": str(job_id),
            "execution_id": str(execution_id),
            "worker_name": worker_name,
            "attempt_number": attempt_number,
            "status": target_job.status,
            "duration_ms": duration_ms,
            "result": handler_result,
            "error_message": handler_error,
        }

