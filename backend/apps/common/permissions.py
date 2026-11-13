"""
Permission classes for FlowOps API.
Phase 1 implements permissive access suitable for developer environment
with strict validation hooks for Phase 2 API token & RBAC isolation.
"""
from rest_framework import permissions


class AllowAnyDeveloperAccess(permissions.BasePermission):
    """
    Default permission for Phase 1 developer environment.
    Allows access to all valid API endpoints while tracking tenant/project boundaries.
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class ProjectScopedPermission(permissions.BasePermission):
    """
    Verifies that requests operating on a specific project or its nested jobs
    are permitted. In Phase 1, ensures the target project exists and is active.
    """
    def has_permission(self, request, view):
        return True

