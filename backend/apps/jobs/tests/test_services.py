import pytest
from apps.projects.models import Project
from apps.jobs.models import Job
from apps.jobs.choices import JobStatus
from apps.jobs.services import JobLifecycleService, JobService
from apps.common.exceptions import InvalidStateTransitionError, ApplicationError, ResourceNotFoundError


@pytest.mark.django_db
class TestJobServices:
    def setup_method(self):
        self.project = Project.objects.create(name="Service Test Project")

    def test_submit_job_service_success(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="email.notification",
            payload={"to": "user@example.com"},
            priority=8,
            status=JobStatus.PENDING,
        )
        assert job.id is not None
        assert job.task_type == "email.notification"
        assert job.status == JobStatus.PENDING
        assert job.priority == 8

    def test_submit_job_service_queued_status(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="doc.process",
            payload={"file": "doc.pdf"},
            priority=3,
            status=JobStatus.QUEUED,
        )
        assert job.status == JobStatus.QUEUED

    def test_submit_job_service_invalid_initial_status(self):
        with pytest.raises(ApplicationError) as exc_info:
            JobService.submit_job(
                project_id=self.project.id,
                task_type="doc.process",
                payload={"file": "doc.pdf"},
                status=JobStatus.COMPLETED,  # Not allowed in Phase 1 submission
            )
        assert exc_info.value.code == "INVALID_INITIAL_STATUS"

    def test_submit_job_service_invalid_priority(self):
        with pytest.raises(ApplicationError) as exc_info:
            JobService.submit_job(
                project_id=self.project.id,
                task_type="doc.process",
                payload={"file": "doc.pdf"},
                priority=11,
            )
        assert exc_info.value.code == "INVALID_PRIORITY"

    def test_submit_job_service_non_existent_project(self):
        fake_uuid = "11111111-1111-1111-1111-111111111111"
        with pytest.raises(ResourceNotFoundError):
            JobService.submit_job(
                project_id=fake_uuid,
                task_type="doc.process",
                payload={"file": "doc.pdf"},
            )

    def test_lifecycle_allowed_transitions(self):
        # 1. PENDING -> QUEUED
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="pipeline.run",
            payload={"stage": 1},
            status=JobStatus.PENDING,
        )
        job = JobLifecycleService.transition(job=job, target_status=JobStatus.QUEUED)
        assert job.status == JobStatus.QUEUED

        # 2. QUEUED -> RUNNING
        job = JobLifecycleService.transition(job=job, target_status=JobStatus.RUNNING)
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None

        # 3. RUNNING -> COMPLETED
        job = JobLifecycleService.transition(
            job=job,
            target_status=JobStatus.COMPLETED,
            result={"summary": "Success", "exit_code": 0},
        )
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.result["exit_code"] == 0

    def test_lifecycle_failure_path(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="faulty.task",
            payload={},
            status=JobStatus.QUEUED,
        )
        job = JobLifecycleService.transition(job=job, target_status=JobStatus.RUNNING)
        job = JobLifecycleService.transition(
            job=job,
            target_status=JobStatus.FAILED,
            error_message="Worker timeout exceeded",
        )
        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert "timeout" in job.error_message

    def test_lifecycle_cancellation_path(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="cancel.me",
            payload={},
            status=JobStatus.PENDING,
        )
        job = JobLifecycleService.transition(job=job, target_status=JobStatus.CANCELLED)
        assert job.status == JobStatus.CANCELLED

    def test_lifecycle_disallowed_transition_raises_error(self):
        # Cannot jump from PENDING directly to COMPLETED without RUNNING
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="jump.test",
            payload={},
            status=JobStatus.PENDING,
        )
        with pytest.raises(InvalidStateTransitionError):
            JobLifecycleService.transition(job=job, target_status=JobStatus.COMPLETED)

    def test_terminal_state_cannot_transition(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="terminal.test",
            payload={},
            status=JobStatus.PENDING,
        )
        job = JobLifecycleService.transition(job=job, target_status=JobStatus.CANCELLED)
        with pytest.raises(InvalidStateTransitionError):
            JobLifecycleService.transition(job=job, target_status=JobStatus.RUNNING)
