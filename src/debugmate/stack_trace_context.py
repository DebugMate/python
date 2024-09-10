import traceback
import os

class StackTraceContext:
    def __init__(self, base_path, exception):
        self.base_path = base_path  # Similar ao 'app->basePath()' no Laravel
        self.exception = exception  # A exceção que será analisada

    def get_context(self):
        trace = []

        # Captura o traceback da exceção
        tb = traceback.extract_tb(self.exception.__traceback__)

        for frame in tb:
            # Obtem o arquivo, a linha e o método
            file_path = frame.filename
            line_number = frame.lineno
            function_name = frame.name
            class_name = self.get_class_name(frame)

            # Verifica se o frame é da aplicação
            application_frame = self.is_application_frame(file_path)

            # Captura o preview das linhas ao redor do erro
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
        # Verificar se frame.locals existe e não é None
        if frame.locals is not None:
            # Tenta obter o nome da classe, se for um método de classe
            class_name = frame.locals.get('self', None)

            if class_name is not None:
                return class_name.__class__.__name__

        # Se frame.locals for None ou não houver 'self', retorna None
        return None

    def is_application_frame(self, file_path):
        """Verifica se o frame pertence ao caminho da aplicação."""
        return file_path.startswith(self.base_path)

    def resolve_file_preview(self, file_path, line_number, snippet_line_count=20):
        """Retorna as linhas de código ao redor da linha do erro."""
        if not os.path.exists(file_path):
            return []

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Determina os limites do snippet
        start_line = max(0, line_number - snippet_line_count // 2 - 1)
        end_line = min(len(lines), line_number + snippet_line_count // 2)

        # Retorna as linhas em formato de lista com o número da linha correspondente
        return {i + 1: line.strip() for i, line in enumerate(lines[start_line:end_line], start=start_line)}
