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

from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
        # Optional: Custom message for 404s
        if response.status_code == 404:
            response.data['detail'] = "The resource you are looking for was not found."

    return response