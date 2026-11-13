import pytest
from rest_framework.test import APIClient
from apps.projects.models import Project
from apps.projects.services import create_project


@pytest.mark.django_db
class TestProjectEndpoints:
    def setup_method(self):
        self.client = APIClient()

    def test_create_project_success(self):
        payload = {
            "name": "E-Commerce Core Service",
            "description": "Handles payment and invoice generation tasks."
        }
        response = self.client.post("/api/v1/projects/", data=payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project created successfully"
        assert data["data"]["name"] == payload["name"]
        assert data["data"]["description"] == payload["description"]
        assert "id" in data["data"]

    def test_create_project_duplicate_name(self):
        create_project(name="Duplicate App", description="First")
        payload = {"name": "Duplicate App", "description": "Second"}
        response = self.client.post("/api/v1/projects/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "name" in data["error"]["details"]

    def test_create_project_missing_name(self):
        payload = {"description": "No name provided"}
        response = self.client.post("/api/v1/projects/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_projects(self):
        create_project(name="Project Alpha")
        create_project(name="Project Beta")
        response = self.client.get("/api/v1/projects/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 2

    def test_retrieve_project_success(self):
        project = create_project(name="Lookup Project", description="Target")
        response = self.client.get(f"/api/v1/projects/{project.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(project.id)
        assert data["data"]["name"] == "Lookup Project"

    def test_retrieve_non_existent_project(self):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/projects/{fake_uuid}/")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    def test_patch_project_success(self):
        project = create_project(name="Original Name", description="Original Desc")
        payload = {"description": "Updated Description"}
        response = self.client.patch(f"/api/v1/projects/{project.id}/", data=payload, format="json")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["description"] == "Updated Description"
        project.refresh_from_db()
        assert project.description == "Updated Description"

    def test_patch_project_unknown_field_rejected(self):
        project = create_project(name="Strict Project")
        payload = {"name": "New Name", "injected_field": "exploit"}
        response = self.client.patch(f"/api/v1/projects/{project.id}/", data=payload, format="json")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "injected_field" in data["error"]["details"]
