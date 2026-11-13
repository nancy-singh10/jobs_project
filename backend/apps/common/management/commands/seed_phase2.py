from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.projects.models import Project
from apps.jobs.models import Job, Execution
from apps.jobs.choices import JobStatus, ExecutionStatus
from apps.jobs.handlers import handle_invoice_generate, handle_email_send


class Command(BaseCommand):
    help = "Seeds Phase 2 execution history and worker telemetry sample data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 2 execution sample data...")

        ecommerce = Project.objects.filter(name="E-Commerce Platform").first()
        if not ecommerce:
            ecommerce = Project.objects.create(name="E-Commerce Platform", description="Retail platform")

        # 1. Successful Completed Job with Execution
        job_comp, _ = Job.objects.get_or_create(
            project=ecommerce,
            task_type="invoice.generate",
            defaults={
                "payload": {"invoice_id": 10428, "customer_email": "jane.doe@example.com", "total_usd": 249.99},
                "status": JobStatus.COMPLETED,
                "priority": 7,
                "started_at": timezone.now() - timedelta(minutes=5),
                "completed_at": timezone.now() - timedelta(minutes=5) + timedelta(milliseconds=142),
                "result": {
                    "invoice_number": "INV-2026-10428",
                    "customer_email": "jane.doe@example.com",
                    "grand_total_usd": 269.99,
                    "pdf_download_url": "https://cdn.flowops.internal/invoices/INV-2026-10428.pdf",
                },
            },
        )
        now = timezone.now()
        start_time_comp = job_comp.started_at or (now - timedelta(minutes=5))
        end_time_comp = job_comp.completed_at or (start_time_comp + timedelta(milliseconds=142))

        Execution.objects.get_or_create(
            job=job_comp,
            attempt_number=1,
            defaults={
                "worker_name": "worker1@flowops-node-01",
                "status": ExecutionStatus.COMPLETED,
                "started_at": start_time_comp,
                "ended_at": end_time_comp,
                "duration_ms": 142,
                "result": job_comp.result,
            },
        )

        # 2. Running Job with Execution
        job_run, _ = Job.objects.get_or_create(
            project=ecommerce,
            task_type="email.send",
            defaults={
                "payload": {"recipient": "alex.smith@example.org", "template": "order_confirmation"},
                "status": JobStatus.RUNNING,
                "priority": 5,
                "started_at": now - timedelta(seconds=12),
            },
        )
        start_time_run = job_run.started_at or (now - timedelta(seconds=12))
        Execution.objects.get_or_create(
            job=job_run,
            attempt_number=1,
            defaults={
                "worker_name": "worker2@flowops-node-02",
                "status": ExecutionStatus.RUNNING,
                "started_at": start_time_run,
            },
        )

        # 3. Failed Job with Execution & Error
        job_fail, _ = Job.objects.get_or_create(
            project=ecommerce,
            task_type="report.generate",
            defaults={
                "payload": {"report_period": "2026-Q3", "simulate_error": True},
                "status": JobStatus.FAILED,
                "priority": 8,
                "started_at": now - timedelta(minutes=2),
                "completed_at": now - timedelta(minutes=2) + timedelta(milliseconds=85),
                "error_message": "Report generation failed: Query memory limit exceeded (simulated).",
            },
        )
        start_time_fail = job_fail.started_at or (now - timedelta(minutes=2))
        end_time_fail = job_fail.completed_at or (start_time_fail + timedelta(milliseconds=85))
        Execution.objects.get_or_create(
            job=job_fail,
            attempt_number=1,
            defaults={
                "worker_name": "worker1@flowops-node-01",
                "status": ExecutionStatus.FAILED,
                "started_at": start_time_fail,
                "ended_at": end_time_fail,
                "duration_ms": 85,
                "error_message": job_fail.error_message or "Simulated error",
            },
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Phase 2 executions!"))
