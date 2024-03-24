from dataclasses import dataclass
from typing import Any
from flet import colors



@dataclass
class ParameterConfigInterface:
    '''
    Интерфейс конфигурации параметра содержит обязательные атрибуты

    key - уникальный ключ параметра
    name - название параметра
    height - высота параметра
    connect_point_color - цвет точки подключения
    '''
    
    key: str = 'unknown'
    name: str = 'Untitled'
    height: int = 20
    default_value: Any = None
    has_connect_point: bool = True
    connect_point_color: str = colors.GREY_500
    tooltip: str = None

    def __post_init__(self):
        if self.key == 'unknown':
            self.key = self.name.lower().replace(" ", "_")
    