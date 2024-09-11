import requests
import traceback
import json
import os
from django.conf import settings
from django.utils.timezone import now
from django.urls import resolve
from debugmate.context.request_context import RequestContext
from debugmate.context.stack_trace_context import StackTraceContext
from debugmate.context.environment_context import EnvironmentContext

class DebugmateAPI:
    @staticmethod
    def send_exception_to_api(exception, request, level='ERROR'):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        exception_location = DebugmateAPI.get_exception_location(exception)

        error_data = {
            "exception": type(exception).__name__,
            "message": str(exception),
            "file": exception_location['file'],
            "line": exception_location['line'],
            "code": 0,
            "resolved_at": None,
            "type": 'web',
            "url": request.build_absolute_uri() if request else '',
            "trace": StackTraceContext(base_path, exception).get_context(),
            "debug": {},
            "app": DebugmateAPI.get_app_context(request, exception),
            "user": DebugmateAPI.get_user_context(request),
            "context": {},
            "request": RequestContext(request).get_context(),
            "environment": EnvironmentContext(request).get_context(),
            "timestamp": now().isoformat(),
            "level": level,
        }

        try:
            response = requests.post(
                settings.DEBUGMATE_API_URL + '/webhook',
                json=error_data,
                headers={
                    'X-DEBUGMATE-TOKEN': settings.DEBUGMATE_API_TOKEN,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=60
            )
        except requests.RequestException:
            pass

    @staticmethod
    def get_app_context(request, exception):
        if request is None:
            return {}

        route_name = request.resolver_match.route
        route_params = request.resolver_match.kwargs
        middlewares = request.META.get('MIDDLEWARE', [])

        return {
            'controller': request.resolver_match.func.__name__,
            'route': {
                'name': route_name,
                'parameters': route_params
            },
            'middlewares': middlewares,
            'view': {
                'name': request.resolver_match.view_name,
                'data': []
            }
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
                'request': {
                    'url': request.build_absolute_uri(),
                    'method': request.method,
                    'curl': self.get_curl(),
                },
                "method": request.method,
                "path": request.path,
                "GET": request.GET.dict(),
                "POST": request.POST.dict(),
                "headers": {k: v for k, v in request.headers.items()},
            }
        return {}

    @staticmethod
    def get_exception_location(exception):
        if exception.__traceback__:
            tb = exception.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            file_name = tb.tb_frame.f_code.co_filename
            line_number = tb.tb_lineno
            code_snippet = exception.__class__.__name__
            return {
                'file': file_name,
                'line': line_number,
                'code_snippet': code_snippet
            }
        return {'file': None, 'line': None, 'code_snippet': None}