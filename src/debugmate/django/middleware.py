import requests
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseServerError
from django.conf import settings
from django.utils.timezone import now

class DebugmateMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)

    def process_request(self, request):
        pass

    def process_exception(self, request, exception):
        self.capture_exception(exception, request)

    def capture_exception(self, exception, request):
        error_data = {
            "exception": type(exception).__name__,
            "message": str(exception),
            "file": exception.__traceback__.tb_frame.f_code.co_filename,
            "line": exception.__traceback__.tb_lineno,
            "code": exception.__class__.__name__,
            "resolved_at": None,
            "type": 'web',
            "url": request.build_absolute_uri(),
            "trace": ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
            "debug": {},
            "app": self.get_app_context(),
            "user": self.get_user_context(request),
            "context": {},
            "request": self.get_request_context(request),
            "environment": settings.DEBUG,
            "timestamp": now().isoformat(),
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

    def get_exception_type(self, exception):
        return "Server Error" if isinstance(exception, Exception) else "Unknown Error"

    def get_app_context(self):
        return {
            "name": "DebugMate",
            "version": "0.1.0",
        }

    def get_user_context(self, request):
        if request.user.is_authenticated:
            return {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        return {}

    def get_request_context(self, request):
        return {
            "method": request.method,
            "path": request.path,
            "GET": request.GET.dict(),
            "POST": request.POST.dict(),
            "headers": {k: v for k, v in request.headers.items()},
        }
