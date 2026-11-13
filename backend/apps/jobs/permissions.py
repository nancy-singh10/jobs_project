from rest_framework import permissions


class JobPermission(permissions.BasePermission):
    """
    Ensures safe access to job endpoints.
    In Phase 1, clients can read and submit jobs. Arbitrary updates (PUT/PATCH)
    are explicitly forbidden at the view layer.
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True

