from django.db import transaction
from apps.projects.models import Project
from apps.projects.selectors import get_project_by_id


def create_project(*, name: str, description: str = "") -> Project:
    """
    Creates a new project record inside an atomic transaction.
    """
    with transaction.atomic():
        project = Project.objects.create(
            name=name.strip(),
            description=description.strip() if description else "",
        )
        return project


def update_project(*, project_id, name: str = None, description: str = None) -> Project:
    """
    Updates an existing project inside an atomic transaction.
    """
    with transaction.atomic():
        project = get_project_by_id(project_id)
        if name is not None:
            project.name = name.strip()
        if description is not None:
            project.description = description.strip()
        project.save()
        return project

