from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Customize default error response
        response.data = {
            "success": False,
            "error": response.data,
            "status_code": response.status_code
        }
        return response

    # Handle not found manually
    if isinstance(exc, Exception):
        return Response({
            "success": False,
            "error": "An unexpected error occurred.",
            "status_code": 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
