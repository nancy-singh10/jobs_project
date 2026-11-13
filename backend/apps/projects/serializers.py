from rest_framework import serializers
from apps.projects.models import Project


class StrictSerializerMixin:
    """
    Mixin to reject any unexpected or unknown fields during deserialization.
    """
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected a JSON object of key-value pairs.")
        unknown_fields = set(data.keys()) - set(self.fields.keys())
        if unknown_fields:
            raise serializers.ValidationError(
                {field: f"Unknown or disallowed field '{field}'." for field in sorted(unknown_fields)}
            )
        return super().to_internal_value(data)


class ProjectSerializer(serializers.ModelSerializer):
    jobs_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "jobs_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "jobs_count", "created_at", "updated_at"]


class ProjectCreateSerializer(StrictSerializerMixin, serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        trim_whitespace=True,
    )

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Project name cannot be empty or whitespace.")
        if Project.objects.filter(name__iexact=cleaned).exists():
            raise serializers.ValidationError(f"A project with the name '{cleaned}' already exists.")
        return cleaned


class ProjectUpdateSerializer(StrictSerializerMixin, serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=False,
        trim_whitespace=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Project name cannot be empty.")
        project_id = self.context.get("project_id")
        if Project.objects.filter(name__iexact=cleaned).exclude(id=project_id).exists():
            raise serializers.ValidationError(f"A project with the name '{cleaned}' already exists.")
        return cleaned

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field ('name' or 'description') must be provided for update.")
        return attrs

