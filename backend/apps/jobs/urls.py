from django.urls import path
from apps.jobs.views import (
    JobListCreateAPIView,
    JobDetailAPIView,
    JobMetricsAPIView,
    JobExecutionListAPIView,
)

app_name = "jobs"

urlpatterns = [
    path("", JobListCreateAPIView.as_view(), name="job-list-create"),
    path("metrics/", JobMetricsAPIView.as_view(), name="job-metrics"),
    path("<uuid:job_id>/", JobDetailAPIView.as_view(), name="job-detail"),
    path("<uuid:job_id>/executions/", JobExecutionListAPIView.as_view(), name="job-executions"),
]

