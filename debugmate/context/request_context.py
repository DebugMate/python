from django.http import HttpRequest
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDictKeyError

class RequestContext:
    def __init__(self, request: HttpRequest):
        self.request = request

    def get_context(self) -> dict:
        return {
            'request': {
                'url': self.request.build_absolute_uri(),
                'method': self.request.method,
                'curl': self.get_curl(),
            },
            'headers': dict(self.request.headers),
            'query_string': self.request.GET.dict(),
            'body': self.get_body(),
            'files': self.get_files(),
            'session': self.get_session(),
            'cookies': self.get_cookies(),
        }

    def get_curl(self) -> str:
        return f"""curl "{self.request.build_absolute_uri()}" \\
    -X {self.request.method} \\
{self.get_curl_headers()}{self.get_curl_body()}"""

    def get_curl_headers(self) -> str:
        headers = ""
        for header, value in self.request.headers.items():
            headers += f"\t-H '{header}: {value}' \\\n"
        return headers

    def get_curl_body(self) -> str:
        body = ""
        all_body = self.get_body()

        # Verifica se o content-type é JSON
        if self.request.content_type == 'application/json':
            return f"\t-d '{json.dumps(all_body)}' \\\n"

        last_key = list(all_body.keys())[-1] if all_body else None
        for label, value in all_body.items():
            body += f"\t-F '{label}={value}'"
            if label != last_key:
                body += " \\\n"

        return body

    def get_body(self) -> dict:
        try:
            return self.request.POST.dict()
        except MultiValueDictKeyError:
            return {}

    def get_files(self) -> dict:
        if not self.request.FILES:
            return {}

        return self.map_files(self.request.FILES.dict())

    def map_files(self, files: dict) -> dict:
        mapped_files = {}
        for key, file in files.items():
            if isinstance(file, list):
                mapped_files[key] = [self.map_file(f) for f in file]
            elif isinstance(file, UploadedFile):
                mapped_files[key] = self.map_file(file)
        return mapped_files

    def map_file(self, file: UploadedFile) -> dict:
        try:
            file_size = file.size
        except RuntimeError:
            file_size = 0

        try:
            mime_type = file.content_type
        except RuntimeError:
            mime_type = 'undefined'

        return {
            'pathname': file.name,
            'size': file_size,
            'mimeType': mime_type,
        }

    def get_session(self) -> dict:
        if self.request.session is None:
            return {}
        return dict(self.request.session.items())

    def get_cookies(self) -> dict:
        return {key: value for key, value in self.request.COOKIES.items() if key not in ['csrftoken', 'sessionid']}