import traceback
import os

class StackTraceContext:
    def __init__(self, base_path, exception):
        self.base_path = base_path
        self.exception = exception

    def get_context(self):
        trace = []

        tb = traceback.extract_tb(self.exception.__traceback__)

        for frame in tb:
            file_path = frame.filename
            line_number = frame.lineno
            function_name = frame.name
            class_name = self.get_class_name(frame)

            application_frame = self.is_application_frame(file_path)

            preview = self.resolve_file_preview(file_path, line_number)

            trace.append({
                'file': file_path,
                'line': line_number,
                'function': function_name,
                'class': class_name,
                'application_frame': application_frame,
                'preview': preview,
            })

        return trace

    def get_class_name(self, frame):
        if frame.locals is not None:
            class_name = frame.locals.get('self', None)

            if class_name is not None:
                return class_name.__class__.__name__
        return None

    def is_application_frame(self, file_path):
        return file_path.startswith(self.base_path)

    def resolve_file_preview(self, file_path, line_number, snippet_line_count=20):
        if not os.path.exists(file_path):
            return []

        with open(file_path, 'r') as f:
            lines = f.readlines()

        start_line = max(0, line_number - snippet_line_count // 2 - 1)
        end_line = min(len(lines), line_number + snippet_line_count // 2)

        return {i + 1: line.strip() for i, line in enumerate(lines[start_line:end_line], start=start_line)}
