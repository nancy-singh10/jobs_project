"""
FlowOps URL Configuration.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.jobs.views import (
    WorkerListAPIView,
    DashboardStatsAPIView,
    HealthCheckAPIView,
)

api_v1_patterns = [
    path("projects/", include("apps.projects.urls", namespace="projects")),
    path("jobs/", include("apps.jobs.urls", namespace="jobs")),
    path("workers/", WorkerListAPIView.as_view(), name="workers"),
    path("dashboard/stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("health/", HealthCheckAPIView.as_view(), name="health"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 endpoints
    path("api/v1/", include((api_v1_patterns, "api-v1"))),
    # OpenAPI Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema-v1"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema-v1"), name="swagger-ui-v1"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema-v1"), name="redoc-v1"),
]

