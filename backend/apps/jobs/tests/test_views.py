import pytest
from rest_framework.test import APIClient
from apps.projects.models import Project
from apps.jobs.models import Job
from apps.jobs.choices import JobStatus
from apps.jobs.services import JobService


@pytest.mark.django_db
class TestJobEndpoints:
    def setup_method(self):
        self.client = APIClient()
        self.project = Project.objects.create(
            name="E-Commerce Storefront",
            description="Production storefront application",
        )
        self.other_project = Project.objects.create(
            name="Analytics Engine",
            description="Data pipeline project",
        )

    def test_submit_job_success(self):
        payload = {
            "project_id": str(self.project.id),
            "task_type": "invoice.generate",
            "payload": {
                "invoice_id": 123,
                "customer_email": "customer@example.com",
            },
            "priority": 5,
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "Job submitted successfully" in data["message"]
        job_data = data["data"]
        assert job_data["task_type"] == "invoice.generate"
        assert job_data["status"] == "PENDING"
        assert job_data["priority"] == 5
        assert "id" in job_data
        assert "created_at" in job_data

        # Verify job is persisted in PostgreSQL
        persisted_job = Job.objects.get(id=job_data["id"])
        assert persisted_job.payload["invoice_id"] == 123
        assert persisted_job.project == self.project

    def test_submit_job_missing_task_type(self):
        payload = {
            "project_id": str(self.project.id),
            "payload": {"invoice_id": 123},
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "task_type" in data["error"]["details"]

    def test_submit_job_invalid_priority_range(self):
        payload = {
            "project_id": str(self.project.id),
            "task_type": "email.send",
            "payload": {"recipient": "test@test.com"},
            "priority": 15,  # Exceeds max 10
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "priority" in data["error"]["details"]

    def test_submit_job_priority_below_one(self):
        payload = {
            "project_id": str(self.project.id),
            "task_type": "email.send",
            "payload": {"recipient": "test@test.com"},
            "priority": 0,
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "priority" in data["error"]["details"]

    def test_submit_job_invalid_payload_type(self):
        # Payload must be a JSON object, not a string or list
        payload = {
            "project_id": str(self.project.id),
            "task_type": "email.send",
            "payload": "invalid string payload",
            "priority": 5,
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "payload" in data["error"]["details"]

    def test_submit_job_non_existent_project(self):
        payload = {
            "project_id": "00000000-0000-0000-0000-000000000000",
            "task_type": "report.export",
            "payload": {"month": "November"},
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "project_id" in data["error"]["details"]

    def test_submit_job_unknown_fields_rejected(self):
        payload = {
            "project_id": str(self.project.id),
            "task_type": "email.send",
            "payload": {},
            "status": "COMPLETED",  # Should be rejected or validated
        }
        response = self.client.post("/api/v1/jobs/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_retrieve_job_success(self):
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="invoice.generate",
            payload={"invoice_id": 999},
            priority=7,
        )
        response = self.client.get(f"/api/v1/jobs/{job.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        job_data = data["data"]
        assert job_data["id"] == str(job.id)
        assert job_data["project_name"] == self.project.name
        assert job_data["payload"]["invoice_id"] == 999
        assert job_data["status"] == "PENDING"
        assert "phase_1_status_note" in job_data

    def test_retrieve_non_existent_job(self):
        fake_uuid = "99999999-9999-9999-9999-999999999999"
        response = self.client.get(f"/api/v1/jobs/{fake_uuid}/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    def test_job_arbitrary_modification_prevented(self):
        # Client cannot arbitrarily mark job COMPLETED via PATCH or PUT
        job = JobService.submit_job(
            project_id=self.project.id,
            task_type="secure.task",
            payload={},
        )
        response_patch = self.client.patch(
            f"/api/v1/jobs/{job.id}/",
            data={"status": "COMPLETED"},
            format="json",
        )
        assert response_patch.status_code == 405

        response_put = self.client.put(
            f"/api/v1/jobs/{job.id}/",
            data={"status": "COMPLETED"},
            format="json",
        )
        assert response_put.status_code == 405

    def test_list_jobs_and_filtering(self):
        # Create jobs across different statuses and task types
        JobService.submit_job(
            project_id=self.project.id,
            task_type="invoice.generate",
            payload={"id": 1},
            status=JobStatus.PENDING,
            priority=5,
        )
        JobService.submit_job(
            project_id=self.project.id,
            task_type="email.send",
            payload={"id": 2},
            status=JobStatus.QUEUED,
            priority=8,
        )
        JobService.submit_job(
            project_id=self.other_project.id,
            task_type="report.generate",
            payload={"id": 3},
            status=JobStatus.PENDING,
            priority=2,
        )

        # 1. Filter by status=QUEUED
        resp = self.client.get("/api/v1/jobs/?status=QUEUED")
        assert resp.status_code == 200
        data = resp.json()["data"]["results"]
        assert len(data) == 1
        assert data[0]["task_type"] == "email.send"

        # 2. Filter by task_type
        resp = self.client.get("/api/v1/jobs/?task_type=invoice.generate")
        assert resp.status_code == 200
        data = resp.json()["data"]["results"]
        assert len(data) == 1
        assert data[0]["task_type"] == "invoice.generate"

        # 3. Filter by project_id
        resp = self.client.get(f"/api/v1/jobs/?project_id={self.other_project.id}")
        assert resp.status_code == 200
        data = resp.json()["data"]["results"]
        assert len(data) == 1
        assert data[0]["project_name"] == "Analytics Engine"

        # 4. Multi-filter: status + priority
        resp = self.client.get("/api/v1/jobs/?status=PENDING&priority=5")
        assert resp.status_code == 200
        data = resp.json()["data"]["results"]
        assert len(data) == 1
        assert data[0]["priority"] == 5

    def test_pagination(self):
        for i in range(15):
            JobService.submit_job(
                project_id=self.project.id,
                task_type=f"batch.item.{i}",
                payload={"index": i},
            )
        response = self.client.get("/api/v1/jobs/?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["results"]) == 5
        assert data["total_pages"] >= 3
        assert data["next"] is not None

    def test_metrics_endpoint(self):
        JobService.submit_job(
            project_id=self.project.id,
            task_type="metrics.job.1",
            payload={},
            status=JobStatus.PENDING,
        )
        JobService.submit_job(
            project_id=self.project.id,
            task_type="metrics.job.2",
            payload={},
            status=JobStatus.QUEUED,
        )

        response = self.client.get("/api/v1/jobs/metrics/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        metrics = data["data"]
        assert metrics["total_jobs"] >= 2
        assert metrics["pending_jobs"] >= 1
        assert metrics["queued_jobs"] >= 1
        assert metrics["completed_jobs"] == 0
        assert metrics["failed_jobs"] == 0
