import platform
import subprocess
import django
from django.conf import settings
from django.http import HttpRequest
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now

class EnvironmentContext:
    def __init__(self, request: HttpRequest):
        self.request = request

    def get_context(self) -> dict:
        return {
            'django_version': django.get_version(),
            'django_locale': settings.LANGUAGE_CODE,
            'django_config_cached': False,
            'app_debug': settings.DEBUG,
            'app_env': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'production',
            'environment_date_time': str(now()),
            'python_version': platform.python_version(),
            'os_version': platform.system(),
            'server_software': self.request.META.get('SERVER_SOFTWARE', ''),
            'database_version': self.get_database_version(),
            'browser_version': self.request.META.get('HTTP_USER_AGENT', ''),
            'node_version': self.run_exec('node', '--version'),
            'npm_version': self.run_exec('npm', '--version'),
        }

    def get_database_version(self) -> str:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
            return f"{connection.vendor} {version[0]}"
        except (ImproperlyConfigured, Exception) as e:
            return ''

    def run_exec(self, alias: str, arguments: str) -> str:
        try:
            result = subprocess.check_output([alias, arguments], stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 'Not Captured'