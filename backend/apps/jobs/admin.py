from django.contrib import admin
from apps.jobs.models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "task_type", "project", "status", "priority", "created_at")
    list_filter = ("status", "priority", "created_at", "project")
    search_fields = ("id", "task_type")
    readonly_fields = ("id", "created_at", "updated_at", "started_at", "completed_at")

