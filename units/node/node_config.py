from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..parameters.parameter_typing import ParameterConfigInterface

from ..data_types import Color

from dataclasses import dataclass, field
from typing import List, Dict, Callable



@dataclass
class NodeConfig:
    """
    Конфигурация узла
    
    key - ключ узла
    name - название узла
    icon - иконка узла
    group - группа узла
    color - цвет узла
    left - позиция узла по оси x
    top - позиция узла по оси y
    width - ширина узла
    enabled - активен ли узел для выбора
    function - функция узла
    parameters - параметры узла
    is_display_result - показывать ли результат узла (используется для узла отображения результата)
    """

    key: str                = "unknown"
    name: str               = "Untitled"
    icon: str               = None
    group: str              = "Default"
    color: str              = Color.random()
    left: int               = 20
    top: int                = 20
    width: int              = 250
    enabled: bool           = True
    function: Callable      = lambda: {}
    parameters: List["ParameterConfigInterface"] = field(default_factory=list)
    is_display_result: bool = False
    
    
    def __post_init__(self):
        for attr in ("key", "name", "group"):
            value = getattr(self, attr)
            if not isinstance(value, str) or not value:
                try:
                    setattr(self, attr, str(value))
                except ValueError:
                    raise ValueError(f"Недопустимый тип {attr}: {type(value)}")
