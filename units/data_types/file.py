from dataclasses import dataclass
import os



@dataclass
class File:
    '''
    Файл
    
    path - путь к файлу
    name - имя файла
    extension - расширение файла
    size - размер файла (байт)
    size_formatted - размер файла в строку
    formatted_name - имя файла и его размер
    data_path - путь к файлу внутри папки "DATA"
    folder - имя папки, в которой находится файл
    '''

    path: str = None

    def __post_init__(self):
        self.name = os.path.basename(self.path)
        self.extension = self.path.split('.')[-1].lower()
        self.size = os.path.getsize(self.path)
        self.size_formatted = self.convert_size(self.size)
        self.formatted_name = f"{self.name} ({self.size_formatted})"
        self.data_path = self.path.replace("DATA\\", "").replace("\\", " > ")
        self.folder = os.path.basename(os.path.dirname(self.path))


    def convert_size(self, size) -> str:
        '''Конвертирует размер файла в байтах в строку'''
        if not size:
            return "0\u00A0байт"
        elif size < 1024:
            return f"{size}\u00A0байт"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f}\u00A0КБ"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f}\u00A0МБ"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f}\u00A0ГБ"
        

    def __eq__(self, other) -> bool:
        if isinstance(other, File):
            return self.path == other.path
        return False
    

    def __str__(self) -> str:
        return self.formatted_name
    