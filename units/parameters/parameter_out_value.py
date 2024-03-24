from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from .parameter_typing import *

from flet import *
from dataclasses import dataclass



@dataclass
class OutParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра выходного типа
    """

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.OUT
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.OUT



class OutParam(Container, ParameterInterface):
    """
    Параметр выходного типа
    """
    
    def __init__(
        self,
        node: 'Node',
        config: OutParamConfig = OutParamConfig()
    ):
        self._type = ParameterType.OUT
        self._connect_type = ParameterConnectType.OUT

        self.node = node
        self._config: OutParamConfig = config
        
        super().__init__()
        self.__post_init__()

        self.content = self._create_content()

        if self._config.has_connect_point:
            self.connect_point = self._create_connect_point()

    
    def _create_content(self) -> Container:
        '''
        Создает содержимое параметра
        '''
        return Container(
            content = Row(
                controls = [
                    Text(self.name),
                ],
                alignment = MainAxisAlignment.END
            ),
            padding = padding.only(left = 5, right = 5),
        )
    