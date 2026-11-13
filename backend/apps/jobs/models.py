import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.projects.models import Project
from apps.jobs.choices import JobStatus, ExecutionStatus


class Job(models.Model):
    """
    Background job entity representing a unit of asynchronous work submitted
    by an external application. In Phase 1, jobs are persisted in PostgreSQL
    with initial lifecycle tracking.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique public job identifier (UUID v4)."
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="jobs",
        db_index=True,
        help_text="The tenant/application project this job belongs to."
    )
    task_type = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Task identifier/routing key, e.g. 'invoice.generate', 'email.send'."
    )
    payload = models.JSONField(
        default=dict,
        help_text="Immutable task parameters and metadata (must be a valid JSON object)."
    )
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
        db_index=True,
        help_text="Current state in the job lifecycle state machine."
    )
    priority = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Job scheduling priority from 1 (lowest) to 10 (highest). Default is 5."
    )
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Execution output/result data populated upon completion (Phase 2)."
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Diagnostic failure details populated if the task fails (Phase 2)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the job was accepted and persisted."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the most recent job update."
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when worker execution started (Phase 2)."
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when job reached a terminal state (Phase 2)."
    )

    class Meta:
        db_table = "flowops_jobs"
        ordering = ["-created_at"]
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        indexes = [
            models.Index(fields=["project", "created_at"], name="job_proj_created_idx"),
            models.Index(fields=["project", "status"], name="job_proj_status_idx"),
            models.Index(fields=["project", "task_type"], name="job_proj_task_idx"),
            models.Index(fields=["status", "priority"], name="job_status_priority_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(priority__gte=1, priority__lte=10),
                name="job_priority_range_1_to_10",
            )
        ]

    def __str__(self):
        return f"Job {self.id} [{self.task_type}] - {self.status}"


class Execution(models.Model):
    """
    Execution record tracking individual worker processing attempts for a job.
    Records worker identity, execution timing, status, result payloads, and errors.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique execution identifier (UUID v4)."
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="executions",
        db_index=True,
        help_text="The associated background job."
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Sequential attempt number for this job."
    )
    worker_name = models.CharField(
        max_length=255,
        default="worker-default",
        db_index=True,
        help_text="Identity/hostname of the worker process that executed this attempt."
    )
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.RUNNING,
        db_index=True,
        help_text="State of this specific execution attempt."
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when worker execution started."
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when worker execution finished."
    )
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total execution duration in milliseconds."
    )
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Execution output returned by the task handler."
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Diagnostic failure details if the attempt failed."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp of record creation."
    )

    class Meta:
        db_table = "flowops_job_executions"
        ordering = ["-started_at"]
        verbose_name = "Job Execution"
        verbose_name_plural = "Job Executions"
        indexes = [
            models.Index(fields=["job", "created_at"], name="exec_job_created_idx"),
            models.Index(fields=["status"], name="exec_status_idx"),
            models.Index(fields=["worker_name"], name="exec_worker_name_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "attempt_number"],
                name="unique_job_attempt_number",
            )
        ]

    def __str__(self):
        return f"Execution {self.id} for Job {self.job_id} [Attempt {self.attempt_number}] - {self.status}"


