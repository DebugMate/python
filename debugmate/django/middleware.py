from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseServerError
from debugmate.utils import DebugmateAPI

class DebugmateMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if not hasattr(request, '_exception_handled'):
            request._exception_handled = True
            DebugmateAPI.send_exception_to_api(exception, request)