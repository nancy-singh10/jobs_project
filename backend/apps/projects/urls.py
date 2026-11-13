from django.urls import path
from apps.projects.views import ProjectListCreateAPIView, ProjectDetailAPIView

app_name = "projects"

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("<uuid:project_id>/", ProjectDetailAPIView.as_view(), name="project-detail"),
]

