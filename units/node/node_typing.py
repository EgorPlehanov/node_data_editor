from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..parameters.parameter_typing import ParamInterface
    from .node_connect_point import NodeConnectPoint

from enum import Enum
from random import choice
from dataclasses import dataclass


class Color(Enum):
    '''Цвет'''
    RED         = "#ff0000"
    PINK        = "#ff0072"
    PURPLE      = "#AA00FF"
    DEEP_PURPLE = "#6a00ff"
    INDIGO      = "#0026ff"
    BLUE        = "#2962FF"
    LIGHT_BLUE  = "#0091EA"
    CYAN        = "#00ddff"
    TEAL        = "#00ffdc"
    GREEN       = "#00ff69"
    LIGHT_GREEN = "#63ff00"
    LIME        = "#bdff00"
    YELLOW      = "#FFD600"
    AMBER       = "#FFAB00"
    ORANGE      = "#FF6D00"
    DEEP_ORANGE = "#DD2C00"

    def __str__(self):
        return str(self.value)
    
    @classmethod
    def random(cls):
        '''Возвращает случайное значение цвета'''
        return choice(list(cls))



@dataclass
class NodeConnection:
    from_param: 'ParamInterface'
    to_param: 'ParamInterface'

    def __post_init__(self):
        self.from_point: "NodeConnectPoint" = self.from_param.connect_point
        self.from_node_id = self.from_point.node_id
        self.from_param_id = self.from_param.id
        self.to_point: "NodeConnectPoint" = self.to_param.connect_point
        self.to_node_id = self.to_point.node_id
        self.to_param_id = self.to_param.id

    def __hash__(self):
        return hash((
            self.from_node_id, self.from_param_id,
            self.to_node_id, self.to_param_id
        ))

    def __eq__(self, other):
        return (
            isinstance(other, NodeConnection)
            and hash(self) == hash(other)
        )
    
    def __str__(self):
        return f"{self.from_node_id}:{self.from_param_id} -> {self.to_node_id}:{self.to_param_id}"
    