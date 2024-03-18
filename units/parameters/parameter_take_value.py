from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from flet import *
from dataclasses import dataclass

from .parameter_typing import *



@dataclass
class TakeValueParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра принимающего значения
    """
    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.TAKE_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN


class TakeValueParam(Container, ParamInterface):
    def __init__(self, node: 'Node', config: TakeValueParamConfig = TakeValueParamConfig()):
        self._type = ParameterType.TAKE_VALUE
        self._connect_type = ParameterConnectType.IN

        self.node = node
        self._config: TakeValueParamConfig = config
        super().__init__()
        self.__post_init__()
        
        self.content = self._create_content()

        if self._config.has_connect_point:
            self.connect_point = self._create_connect_point()

    
    def _create_content(self):
        '''
        Создает содержимое параметра
        '''
        return Container(
            content = Row([
                Text(self.name)
            ]),
            padding = padding.only(left = 5, right = 5),
        )