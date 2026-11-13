import pytest
from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APIClient
from apps.projects.models import Project
from apps.jobs.models import Job, Execution
from apps.jobs.choices import JobStatus, ExecutionStatus
from apps.jobs.services import JobService, dispatch_job_task
from apps.jobs.execution_service import JobExecutionService
from apps.jobs.handlers import (
    handle_invoice_generate,
    handle_email_send,
    handle_report_generate,
    get_task_handler,
    TaskExecutionError,
)


@pytest.mark.django_db
class TestTaskHandlers:
    def test_invoice_handler_success(self):
        payload = {"invoice_id": 55, "customer_email": "test@domain.com", "total_usd": 100}
        result = handle_invoice_generate(payload)
        assert result["invoice_number"] == "INV-2026-55"
        assert result["customer_email"] == "test@domain.com"
        assert result["subtotal_usd"] == 100.0
        assert result["tax_usd"] == 8.0
        assert result["grand_total_usd"] == 108.0
        assert "pdf_download_url" in result

    def test_invoice_handler_simulated_error(self):
        payload = {"invoice_id": 55, "simulate_error": True}
        with pytest.raises(TaskExecutionError) as exc:
            handle_invoice_generate(payload)
        assert "tax engine service unreachable" in str(exc.value)

    def test_email_handler_success(self):
        payload = {"recipient": "client@example.com", "template": "receipt"}
        result = handle_email_send(payload)
        assert result["recipient"] == "client@example.com"
        assert result["delivery_status"] == "DELIVERED"
        assert "<msg-" in result["message_id"]

    def test_report_handler_success(self):
        payload = {"report_period": "2026-Q4", "format": "pdf"}
        result = handle_report_generate(payload)
        assert result["report_period"] == "2026-Q4"
        assert result["format"] == "pdf"
        assert result["records_aggregated"] > 0

    def test_unregistered_handler_raises_error(self):
        with pytest.raises(TaskExecutionError) as exc:
            get_task_handler("malicious.arbitrary.code")
        assert "Unsupported task type" in str(exc.value)


@pytest.mark.django_db
class TestJobExecutionService:
    def setup_method(self):
        self.project = Project.objects.create(name="Phase 2 Test Project")

    def test_execute_job_success_flow(self):
        job = Job.objects.create(
            project=self.project,
            task_type="invoice.generate",
            payload={"invoice_id": 777, "total_usd": 200},
            status=JobStatus.PENDING,
        )

        res = JobExecutionService.execute_job(
            job_id=str(job.id),
            worker_name="worker-alpha@node-1",
        )

        assert res["success"] is True
        assert res["worker_name"] == "worker-alpha@node-1"
        assert res["duration_ms"] > 0
        assert res["status"] == JobStatus.COMPLETED

        job.refresh_from_db()
        assert job.status == JobStatus.COMPLETED
        assert job.started_at is not None
        assert job.completed_at is not None
        assert job.result["invoice_number"] == "INV-2026-777"

        # Check execution history record
        execution = Execution.objects.get(id=res["execution_id"])
        assert execution.job == job
        assert execution.worker_name == "worker-alpha@node-1"
        assert execution.attempt_number == 1
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.result["invoice_number"] == "INV-2026-777"
        assert execution.duration_ms > 0

    def test_execute_job_failure_flow(self):
        job = Job.objects.create(
            project=self.project,
            task_type="email.send",
            payload={"recipient": "fail@user.com", "simulate_error": True},
            status=JobStatus.QUEUED,
        )

        res = JobExecutionService.execute_job(
            job_id=str(job.id),
            worker_name="worker-beta@node-2",
        )

        assert res["success"] is False
        assert res["status"] == JobStatus.FAILED
        assert "Mailbox quota exceeded" in res["error_message"]

        job.refresh_from_db()
        assert job.status == JobStatus.FAILED
        assert job.error_message is not None

        execution = Execution.objects.get(id=res["execution_id"])
        assert execution.status == ExecutionStatus.FAILED
        assert "Mailbox quota exceeded" in execution.error_message

    def test_terminal_job_cannot_be_re_executed(self):
        job = Job.objects.create(
            project=self.project,
            task_type="invoice.generate",
            payload={},
            status=JobStatus.COMPLETED,
        )

        res = JobExecutionService.execute_job(job_id=str(job.id))
        assert res["success"] is False
        assert "terminal state" in res["message"]
        assert Execution.objects.filter(job=job).count() == 0

    def test_cancelled_job_cannot_be_executed(self):
        job = Job.objects.create(
            project=self.project,
            task_type="report.generate",
            payload={},
            status=JobStatus.CANCELLED,
        )

        res = JobExecutionService.execute_job(job_id=str(job.id))
        assert res["success"] is False
        assert Execution.objects.filter(job=job).count() == 0

    def test_multiple_workers_execution_recording(self):
        job1 = Job.objects.create(project=self.project, task_type="email.send", payload={"id": 1})
        job2 = Job.objects.create(project=self.project, task_type="email.send", payload={"id": 2})

        res1 = JobExecutionService.execute_job(job_id=str(job1.id), worker_name="worker-1@hostA")
        res2 = JobExecutionService.execute_job(job_id=str(job2.id), worker_name="worker-2@hostB")

        assert res1["worker_name"] == "worker-1@hostA"
        assert res2["worker_name"] == "worker-2@hostB"

        exec1 = Execution.objects.get(job=job1)
        exec2 = Execution.objects.get(job=job2)
        assert exec1.worker_name == "worker-1@hostA"
        assert exec2.worker_name == "worker-2@hostB"


@pytest.mark.django_db
class TestJobDispatchAndAPIs:
    def setup_method(self):
        self.client = APIClient()
        self.project = Project.objects.create(name="Phase 2 API Project")

    @pytest.mark.django_db(transaction=True)
    def test_submit_job_triggers_celery_dispatch(self):
        with patch("apps.jobs.services.dispatch_job_task") as mock_dispatch:
            payload = {
                "project_id": str(self.project.id),
                "task_type": "invoice.generate",
                "payload": {"id": 1},
                "priority": 6,
            }
            res = self.client.post("/api/v1/jobs/", data=payload, format="json")
            assert res.status_code == 201
            assert mock_dispatch.called

    def test_dispatch_broker_unavailable_failure_handling(self):
        job = Job.objects.create(
            project=self.project,
            task_type="invoice.generate",
            payload={},
            status=JobStatus.PENDING,
        )

        with patch("apps.jobs.tasks.process_job.delay", side_effect=Exception("Redis connection refused")):
            success = dispatch_job_task(str(job.id))
            assert success is False
            job.refresh_from_db()
            assert job.status == JobStatus.PENDING
            assert "Broker dispatch warning" in job.error_message

    def test_executions_history_endpoint(self):
        job = Job.objects.create(
            project=self.project,
            task_type="invoice.generate",
            payload={"invoice_id": 999},
        )
        JobExecutionService.execute_job(job_id=str(job.id), worker_name="worker-hist@test")

        res = self.client.get(f"/api/v1/jobs/{job.id}/executions/")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["worker_name"] == "worker-hist@test"
        assert data["data"][0]["status"] == "COMPLETED"

    def test_job_detail_endpoint_includes_executions(self):
        job = Job.objects.create(
            project=self.project,
            task_type="report.generate",
            payload={},
        )
        JobExecutionService.execute_job(job_id=str(job.id), worker_name="worker-detail@test")

        res = self.client.get(f"/api/v1/jobs/{job.id}/")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["execution_count"] == 1
        assert data["latest_execution"]["worker_name"] == "worker-detail@test"
        assert len(data["executions"]) == 1

    def test_workers_endpoint(self):
        res = self.client.get("/api/v1/workers/")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "workers" in data["data"]

    def test_dashboard_stats_endpoint(self):
        res = self.client.get("/api/v1/dashboard/stats/")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        stats = data["data"]
        assert "total_jobs" in stats
        assert "running_jobs" in stats
        assert "completed_jobs" in stats
        assert "failed_jobs" in stats
        assert "avg_duration_ms" in stats
        assert "recent_executions" in stats

    def test_health_check_endpoint(self):
        res = self.client.get("/api/v1/health/")
        assert res.status_code in [200, 503]
        data = res.json()
        assert "data" in data
        assert "database" in data["data"]
        assert "redis" in data["data"]
        assert data["data"]["database"]["status"] == "healthy"
