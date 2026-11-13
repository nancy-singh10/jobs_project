import json
from rest_framework import serializers
from django.conf import settings
from drf_spectacular.utils import extend_schema_field
from apps.jobs.models import Job, Execution
from apps.jobs.choices import JobStatus, ExecutionStatus
from apps.projects.selectors import project_exists
from apps.projects.serializers import StrictSerializerMixin


class JobSubmitRequestSerializer(StrictSerializerMixin, serializers.Serializer):
    """
    Request serializer for submitting background jobs to FlowOps.
    Validates payload structure, project foreign key, priority range,
    and rejects extraneous fields.
    """
    project_id = serializers.UUIDField(
        required=True,
        help_text="UUID of the registered Project submitting this task."
    )
    task_type = serializers.CharField(
        max_length=255,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        help_text="Task identifier, e.g. 'invoice.generate'."
    )
    payload = serializers.JSONField(
        required=True,
        help_text="JSON object containing task parameters."
    )
    priority = serializers.IntegerField(
        required=False,
        default=5,
        min_value=1,
        max_value=10,
        help_text="Priority level from 1 (lowest) to 10 (highest). Defaults to 5."
    )
    status = serializers.ChoiceField(
        choices=[JobStatus.PENDING, JobStatus.QUEUED],
        required=False,
        default=JobStatus.PENDING,
        help_text="Initial submission state: 'PENDING' (default) or 'QUEUED'."
    )

    def validate_project_id(self, value):
        if not project_exists(value):
            raise serializers.ValidationError(f"Project with ID '{value}' does not exist.")
        return value

    def validate_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload must be a valid JSON object (dictionary).")
        
        # Check payload size against limits
        try:
            serialized_size = len(json.dumps(value).encode("utf-8"))
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(f"Invalid JSON in payload: {str(e)}")

        max_size = getattr(settings, "MAX_PAYLOAD_SIZE_BYTES", 524288)
        if serialized_size > max_size:
            raise serializers.ValidationError(
                f"Payload size exceeds allowed maximum limit of {max_size} bytes."
            )
        return value

    def validate_task_type(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Task type is mandatory and cannot be empty.")
        return cleaned


class JobSubmitResponseDataSerializer(serializers.ModelSerializer):
    """
    Response schema returned immediately upon successful job ingestion.
    """
    class Meta:
        model = Job
        fields = [
            "id",
            "task_type",
            "status",
            "priority",
            "created_at",
        ]


class JobListSerializer(serializers.ModelSerializer):
    """
    Compact job representation for listing and tabular views.
    """
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_id = serializers.UUIDField(source="project.id", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "project_id",
            "project_name",
            "task_type",
            "status",
            "priority",
            "created_at",
        ]


class ExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for individual worker execution attempts.
    """
    class Meta:
        model = Execution
        fields = [
            "id",
            "job_id",
            "attempt_number",
            "worker_name",
            "status",
            "started_at",
            "ended_at",
            "duration_ms",
            "result",
            "error_message",
            "created_at",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """
    Full job entity representation including payload, results, diagnostics,
    and associated worker execution attempts.
    """
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_id = serializers.UUIDField(source="project.id", read_only=True)
    execution_count = serializers.SerializerMethodField()
    latest_execution = serializers.SerializerMethodField()
    executions = ExecutionSerializer(many=True, read_only=True)
    phase_1_status_note = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "project_id",
            "project_name",
            "task_type",
            "payload",
            "status",
            "priority",
            "result",
            "error_message",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
            "execution_count",
            "latest_execution",
            "executions",
            "phase_1_status_note",
        ]

    @extend_schema_field(serializers.CharField())
    def get_phase_1_status_note(self, obj):
        return "Phase 2 background worker execution enabled via Redis message broker."

    @extend_schema_field(serializers.IntegerField())
    def get_execution_count(self, obj):
        return obj.executions.count()

    @extend_schema_field(ExecutionSerializer(allow_null=True))
    def get_latest_execution(self, obj):
        latest = obj.executions.first()
        return ExecutionSerializer(latest).data if latest else None



class JobMetricsSerializer(serializers.Serializer):
    """
    Dashboard metric summary serializer.
    """
    total_jobs = serializers.IntegerField()
    pending_jobs = serializers.IntegerField()
    queued_jobs = serializers.IntegerField()
    running_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    cancelled_jobs = serializers.IntegerField()
