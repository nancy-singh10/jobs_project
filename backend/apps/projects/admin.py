from django.contrib import admin
from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "created_at", "updated_at")
    search_fields = ("name", "id")
    readonly_fields = ("id", "created_at", "updated_at")

