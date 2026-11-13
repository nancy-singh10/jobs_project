"""
Common utility functions for response formatting and payload validation.
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Request successful", status_code=status.HTTP_200_OK):
    """
    Constructs a standardized success JSON response envelope.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )

