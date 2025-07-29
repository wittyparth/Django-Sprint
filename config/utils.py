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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
# utils.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def generate_verification_token(user_id):
    return signer.sign(str(user_id))

def verify_token(token, max_age=60*60*24):  # 24 hours
    try:
        value = signer.unsign(token, max_age=max_age)
        return int(value)
    except (BadSignature, SignatureExpired):
        return None
