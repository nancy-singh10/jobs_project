from django.db import models


class JobStatus(models.TextChoices):
    """
    Job lifecycle states.
    In Phase 1, only PENDING and QUEUED states are assigned upon submission.
    In Phase 2, workers transition jobs through RUNNING to COMPLETED or FAILED.
    """
    PENDING = "PENDING", "Pending"
    QUEUED = "QUEUED", "Queued"
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class ExecutionStatus(models.TextChoices):
    """
    Individual worker execution attempt states.
    """
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


