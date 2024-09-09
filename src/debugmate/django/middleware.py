import requests
import traceback

from django.http import HttpResponseServerError

class DebugmateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Process the request
            response = self.get_response(request)
        except Exception as e:
            # Capture and send error data
            self.capture_exception(e, request)
            # Return a generic server error response
            return HttpResponseServerError("A server error occurred.")
        return response

    def capture_exception(self, exception, request):
        error_data = {
            "exception": type(exception).__name__,
            "message": str(exception),
            "path": request.path,
            "traceback": ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
            "method": request.method,
        }
        # Send error details to an external service
        try:
            requests.post(
                "https://laravel-new.test",
                json=error_data,
                headers={
                    'X-DEBUGMATE-TOKEN': 'a674a5f4-cd5e-4e40-9ce1-e9eb575caa1a',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            )
        except requests.RequestException as e:
            # Log the failure or handle it appropriately
            print(f"Failed to report error: {e}")