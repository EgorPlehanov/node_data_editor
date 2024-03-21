from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from abc import ABC, abstractmethod
from typing import Any
from enum import Enum
from itertools import count
from dataclasses import dataclass
from flet import colors
import os

from ..node.node_connect_point import NodeConnectPoint, ParameterConnectType



class ParameterType(Enum):
    '''
    Типы параметров
    '''
    OUT = 'out'
    SINGLE_VALUE = 'single_value'
    TAKE_VALUE = 'take_value'
    BOOL_VALUE = 'bool_value'
    TEXT_VALUE = 'text_value'
    FILE_PICKER_VALUE = 'file_picker_value'
    DROPDOWN_VALUE = 'dropdown_value'

    def __str__(self):
        return self.value



@dataclass
class ParameterConfigInterface:
    '''
    Интерфейс конфигурации параметра

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



class ParamInterface(ABC):
    '''
    Интерфейс параметра
    '''
    id_counter = count()

    PADDING_VERTICAL_SIZE = 1
    
    MAIN_COLOR = colors.with_opacity(0.05, colors.WHITE)
    HOVER_COLOR = colors.with_opacity(0.2, colors.WHITE)
    ACCENT_COLOR = colors.DEEP_ORANGE_ACCENT_400
    
    _type: ParameterType = None
    _connect_type: ParameterConnectType = None
    _config: Any = None

    node: 'Node' = None

    _key: str = None
    name: str = None
    has_connect_point: bool = False
    connect_point_color: str = None
    
    connect_point: NodeConnectPoint = None

    def __init__(self):
        self.id = next(self.id_counter)

        self._key = self._config.key
        self.name = self._config.name
        self.has_connect_point = self._config.has_connect_point
        self.connect_point_color = self._config.connect_point_color
        self.is_connected = False
        self.value = self._config.default_value

    def __post_init__(self):
        self.height = self._config.height
        self.control_height = self.height - self.PADDING_VERTICAL_SIZE * 2
        self.tooltip = self._config.tooltip

    def __eq__(self, other):
        return (isinstance(other, ParamInterface) and self.id == other.id)
    
    def __hash__(self):
        return hash(self.id)

    @property
    def type(self) -> str:
        return self._type
    
    @abstractmethod
    def _create_content(self) -> Any:
        pass

    def set_connect_state(self, is_connected: bool, is_recalculate: bool = True) -> None:
        self.is_connected = is_connected
        if is_recalculate:
            self._on_change()
    
    def _on_change(self) -> None:
        self.node.calculate()

    def _create_connect_point(self) -> NodeConnectPoint:
        return NodeConnectPoint(
            node = self.node,
            parameter = self,
            id = self.id,
            connect_type = self._connect_type,
            color = self.connect_point_color,
        )

    def set_connect_point_coordinates(
        self,
        open_top: int,
        open_left: int,
        close_top: int,
        close_left: int
    ) -> None:
        connect_point = self.connect_point
        if connect_point is not None:
            connect_point.top = open_top
            connect_point.left = open_left
            connect_point.open_top = open_top
            connect_point.open_left = open_left
            connect_point.close_top = close_top
            connect_point.close_left = close_left



@dataclass
class File:
    '''Файл
    
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
        
    def __eq__(self, other):
        if isinstance(other, File):
            return self.path == other.path
        return False
    
    def __str__(self) -> str:
        return self.formatted_name
    