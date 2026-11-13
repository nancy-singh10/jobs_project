from django.db.models import Count, QuerySet
from apps.projects.models import Project
from apps.common.exceptions import ResourceNotFoundError


def list_projects() -> QuerySet[Project]:
    """
    Returns all projects annotated with their related job count.
    """
    return Project.objects.annotate(jobs_count=Count("jobs")).order_by("-created_at")


def get_project_by_id(project_id) -> Project:
    """
    Retrieves a single project by UUID or raises ResourceNotFoundError.
    """
    try:
        return Project.objects.annotate(jobs_count=Count("jobs")).get(id=project_id)
    except (Project.DoesNotExist, ValueError):
        raise ResourceNotFoundError(f"Project with ID '{project_id}' does not exist.")


def project_exists(project_id) -> bool:
    """
    Checks if a project exists by its UUID.
    """
    try:
        return Project.objects.filter(id=project_id).exists()
    except (ValueError, TypeError):
        return False

