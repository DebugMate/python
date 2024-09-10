import requests
import traceback
from django.conf import settings
from django.utils.timezone import now

class DebugmateAPI:
    @staticmethod
    def send_exception_to_api(exception, request, level='ERROR'):
        error_data = {
            "exception": type(exception).__name__,
            "message": str(exception),
            "file": exception.__traceback__.tb_frame.f_code.co_filename,
            "line": exception.__traceback__.tb_lineno,
            "code": exception.__class__.__name__,
            "resolved_at": None,
            "type": 'web',
            "url": request.build_absolute_uri() if request else '',
            "trace": ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
            "debug": {},
            "app": DebugmateAPI.get_app_context(),
            "user": DebugmateAPI.get_user_context(request),
            "context": {},
            "request": DebugmateAPI.get_request_context(request),
            "environment": settings.DEBUG,
            "timestamp": now().isoformat(),
            "level": level,
        }
        try:
            response = requests.post(
                settings.DEBUGMATE_API_URL + '/api/capture',
                json=error_data,
                headers={
                    'X-DEBUGMATE-TOKEN': settings.DEBUGMATE_API_TOKEN,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=5
            )
        except requests.RequestException:
            pass

    @staticmethod
    def get_app_context():
        return {
            "name": "DebugMate",
            "version": "0.1.0",
        }

    @staticmethod
    def get_user_context(request):
        if request and request.user.is_authenticated:
            return {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        return {}

    @staticmethod
    def get_request_context(request):
        if request:
            return {
                "method": request.method,
                "path": request.path,
                "GET": request.GET.dict(),
                "POST": request.POST.dict(),
                "headers": {k: v for k, v in request.headers.items()},
            }
        return {}