import logging
from debugmate.utils import DebugmateAPI

class DebugmateHandler(logging.Handler):
    def emit(self, record):
        request = getattr(record, 'request', None)
        if request and hasattr(request, '_exception_handled'):
            return

        exception = record.exc_info[1] if record.exc_info else None
        if exception:
            DebugmateAPI.send_exception_to_api(exception, request, level=record.levelname)