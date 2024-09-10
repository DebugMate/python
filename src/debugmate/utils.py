import requests
import traceback
import json
import os
from django.conf import settings
from django.utils.timezone import now
from django.urls import resolve
from django.template import TemplateDoesNotExist
from debugmate.request_context import RequestContext
from debugmate.stack_trace_context import StackTraceContext

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
            "code": exception_location['code_snippet'],
            "resolved_at": None,
            "type": 'web',
            "url": request.build_absolute_uri() if request else '',
            "trace": StackTraceContext(base_path, exception).get_context(),
            "debug": {},
            "app": DebugmateAPI.get_app_context(request, exception),
            "user": DebugmateAPI.get_user_context(request),
            "context": {},
            "request": RequestContext(request).get_context(),
            "environment": DebugmateAPI.get_environment_settings(),
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
    def get_app_context(request, exception):
        # Verifica se a aplicação está rodando no console
        if request is None:
            return {}

        # Captura detalhes da rota e do controlador (view)
        route_name = request.resolver_match.view_name
        route_params = request.resolver_match.kwargs
        middlewares = request.META.get('MIDDLEWARE', [])

        # Verifica se a exceção está relacionada a uma View (pode ser ajustado conforme a lógica do seu projeto)
        is_view_exception = isinstance(exception, TemplateDoesNotExist)

        return {
            'controller': request.resolver_match.func.__name__,
            'route': {
                'name': route_name,
                'parameters': route_params
            },
            'middlewares': middlewares,
            'view': {
                'name': exception.template_name if is_view_exception else None,
                'data': list(exception.args) if is_view_exception else []
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

    def get_environment_settings():
        # Seleciona algumas configurações relevantes do Django para enviar como JSON
        environment_settings = {
            "DEBUG": settings.DEBUG,
            "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
            "INSTALLED_APPS": settings.INSTALLED_APPS,
            "DATABASES": settings.DATABASES,
            "MIDDLEWARE": settings.MIDDLEWARE,
            "TEMPLATES": settings.TEMPLATES,
            "TIME_ZONE": settings.TIME_ZONE,
            "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        }
        # Converte as configurações para JSON para o campo `environment`
        return json.dumps(environment_settings, default=str)  # Converte para string JSON

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