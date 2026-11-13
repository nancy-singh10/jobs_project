"""
Standardized exception handling for FlowOps API.
Conforms to Phase 1 specification:
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable summary",
    "details": {}
  }
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    MethodNotAllowed,
    UnsupportedMediaType,
    ParseError,
)
import logging

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Base application exception for domain/service level errors."""
    def __init__(self, message, code="BAD_REQUEST", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code


class ResourceNotFoundError(ApplicationError):
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message=message, code="NOT_FOUND", details=details, status_code=status.HTTP_404_NOT_FOUND)


class InvalidStateTransitionError(ApplicationError):
    def __init__(self, message="Invalid job state transition", details=None):
        super().__init__(message=message, code="INVALID_STATE_TRANSITION", details=details, status_code=status.HTTP_400_BAD_REQUEST)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that guarantees consistent error responses
    without leaking internal stack traces or database errors.
    """
    if isinstance(exc, ApplicationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
            status=exc.status_code,
        )

    # Let DRF handle standard REST exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        code = "APPLICATION_ERROR"
        message = "An error occurred while processing the request."
        details = response.data

        if isinstance(exc, ValidationError):
            code = "VALIDATION_ERROR"
            message = "Invalid request data. Please check the details provided."
        elif isinstance(exc, NotFound):
            code = "NOT_FOUND"
            message = "The requested resource was not found."
        elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            code = "AUTHENTICATION_ERROR"
            message = "Authentication credentials were not provided or are invalid."
        elif isinstance(exc, PermissionDenied):
            code = "PERMISSION_DENIED"
            message = "You do not have permission to perform this action."
        elif isinstance(exc, MethodNotAllowed):
            code = "METHOD_NOT_ALLOWED"
            message = f"Method '{context['request'].method}' not allowed."
        elif isinstance(exc, ParseError):
            code = "MALFORMED_REQUEST"
            message = "Malformed request payload."

        response.data = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details if isinstance(details, dict) else {"non_field_errors": details},
            },
        }
        return response

    # Unhandled 500 errors - do NOT leak stack traces
    logger.exception("Unhandled server error: %s", exc, exc_info=True)
    return Response(
        {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred. Please contact support.",
                "details": {},
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

