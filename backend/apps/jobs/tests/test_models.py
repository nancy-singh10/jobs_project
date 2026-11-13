import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from apps.projects.models import Project
from apps.jobs.models import Job
from apps.jobs.choices import JobStatus


@pytest.mark.django_db
class TestJobModel:
    def setup_method(self):
        self.project = Project.objects.create(name="Model Test Project")

    def test_job_creation_default_values(self):
        job = Job.objects.create(
            project=self.project,
            task_type="report.generate",
            payload={"report_id": 42},
        )
        assert job.status == JobStatus.PENDING
        assert job.priority == 5
        assert job.result is None
        assert job.error_message is None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.id is not None
        assert job.project == self.project
        assert str(job.id) in str(job)

    def test_job_priority_validation(self):
        # Priority must be between 1 and 10
        job_invalid = Job(
            project=self.project,
            task_type="invalid.priority",
            payload={},
            priority=15,
        )
        with pytest.raises(ValidationError):
            job_invalid.full_clean()
