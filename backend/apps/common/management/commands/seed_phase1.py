from django.core.management.base import BaseCommand
from apps.projects.models import Project
from apps.jobs.models import Job
from apps.jobs.choices import JobStatus


class Command(BaseCommand):
    help = "Seeds PostgreSQL with realistic sample projects and Phase 1 jobs."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 1 sample data...")

        ecommerce, _ = Project.objects.get_or_create(
            name="E-Commerce Platform",
            defaults={"description": "High-volume retail checkout, invoice generation and dispatch engine."},
        )
        fintech, _ = Project.objects.get_or_create(
            name="Fintech Settlement Hub",
            defaults={"description": "Banking reconciliation and batch transaction ledger processing."},
        )
        edtech, _ = Project.objects.get_or_create(
            name="EdTech Learning System",
            defaults={"description": "Course completion certificates and automated student analytics."},
        )

        sample_jobs = [
            {
                "project": ecommerce,
                "task_type": "invoice.generate",
                "payload": {"invoice_id": 10428, "customer_email": "jane.doe@example.com", "total_usd": 249.99},
                "status": JobStatus.PENDING,
                "priority": 7,
            },
            {
                "project": ecommerce,
                "task_type": "email.send",
                "payload": {"template": "order_confirmation", "recipient": "alex.smith@example.org"},
                "status": JobStatus.PENDING,
                "priority": 5,
            },
            {
                "project": fintech,
                "task_type": "report.create",
                "payload": {"report_period": "2026-Q3", "reconciliation_code": "BATCH-9021"},
                "status": JobStatus.PENDING,
                "priority": 8,
            },
            {
                "project": fintech,
                "task_type": "data.synchronize",
                "payload": {"ledger_id": "LDG-8812", "target_system": "core_banking"},
                "status": JobStatus.QUEUED,
                "priority": 6,
            },
            {
                "project": edtech,
                "task_type": "document.process",
                "payload": {"certificate_id": "CERT-2026-X1", "student_id": 9921, "format": "pdf"},
                "status": JobStatus.PENDING,
                "priority": 4,
            },
            {
                "project": ecommerce,
                "task_type": "notification.push",
                "payload": {"user_id": 4810, "channel": "fcm", "title": "Your order has shipped"},
                "status": JobStatus.QUEUED,
                "priority": 3,
            },
        ]

        created_count = 0
        for item in sample_jobs:
            if not Job.objects.filter(project=item["project"], task_type=item["task_type"]).exists():
                Job.objects.create(**item)
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded! Projects: 3, Initial Phase 1 jobs created: {created_count}."
        ))
