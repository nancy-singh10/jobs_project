import uuid
from django.db import models


class Project(models.Model):
    """
    Project entity representing an external tenant or application domain
    submitting background tasks to FlowOps.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the project (UUID v4)."
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Human-readable unique project name."
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional summary of the project scope and workload."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the project was registered."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the most recent project update."
    )

    class Meta:
        db_table = "flowops_projects"
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

