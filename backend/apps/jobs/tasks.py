"""
Celery background worker tasks for FlowOps Phase 2.
"""
import logging
from celery import shared_task
from apps.jobs.execution_service import JobExecutionService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.jobs.tasks.process_job",
    max_retries=0,  # Phase 2 has single-attempt execution; retries are Phase 4
    acks_late=True,
)
def process_job(self, job_id: str, worker_name: str = None):
    """
    Asynchronous Celery task consumed by background workers.
    Receives only the serializable UUID string, invokes the execution service,
    and updates PostgreSQL with execution duration and state.
    """
    resolved_worker = worker_name or getattr(self.request, "hostname", "worker-default")
    logger.info("Worker '%s' processing job '%s'", resolved_worker, job_id)

    return JobExecutionService.execute_job(
        job_id=job_id,
        worker_name=resolved_worker,
    )

