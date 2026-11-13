from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.projects.selectors import list_projects, get_project_by_id
from apps.projects.services import create_project, update_project
from apps.projects.serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
)
from apps.common.utils import success_response


class ProjectListCreateAPIView(APIView):
    """
    List registered projects or register a new project.
    """

    @extend_schema(
        operation_id="list_projects",
        summary="List all projects",
        description="Retrieves a list of all active projects, annotated with total job counts.",
        responses={200: ProjectSerializer(many=True)},
    )
    def get(self, request):
        projects = list_projects()
        serializer = ProjectSerializer(projects, many=True)
        return success_response(
            data=serializer.data,
            message="Projects retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="create_project",
        summary="Create a new project",
        description="Creates a new project record in PostgreSQL inside an atomic transaction.",
        request=ProjectCreateSerializer,
        responses={
            201: ProjectSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = create_project(**serializer.validated_data)
        return success_response(
            data=ProjectSerializer(project).data,
            message="Project created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class ProjectDetailAPIView(APIView):
    """
    Retrieve or partially update project details.
    """

    @extend_schema(
        operation_id="retrieve_project",
        summary="Retrieve project details",
        description="Fetches full details of a project by its unique UUID.",
        responses={
            200: ProjectSerializer,
            404: OpenApiResponse(description="Project not found"),
        },
    )
    def get(self, request, project_id):
        project = get_project_by_id(project_id)
        return success_response(
            data=ProjectSerializer(project).data,
            message="Project retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="update_project",
        summary="Update project details",
        description="Partially updates an existing project name or description.",
        request=ProjectUpdateSerializer,
        responses={
            200: ProjectSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Project not found"),
        },
    )
    def patch(self, request, project_id):
        serializer = ProjectUpdateSerializer(
            data=request.data,
            context={"project_id": project_id},
        )
        serializer.is_valid(raise_exception=True)
        project = update_project(
            project_id=project_id,
            **serializer.validated_data,
        )
        return success_response(
            data=ProjectSerializer(project).data,
            message="Project updated successfully",
            status_code=status.HTTP_200_OK,
        )

