from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..parameters.parameter_typing.parameter_connect_point import ParameterConnectPoint
    from ..parameters import ParameterInterface
    from ..node_area import NodeArea
    from .node import Node

from flet import *
import flet.canvas as cv
from typing import List, Tuple



class NodeConnection:
    """
    Соединение двух параметров

    содержит ссылки на источник и принимающий параметр,
    а также объект пути их соединения
    """

    LINE_LEN: int = 10
    STEEPNESS: int = 70

    def __init__(
        self,
        from_param: "ParameterInterface",
        to_param: "ParameterInterface"
    ):
        self.node_area: "NodeArea" = from_param.node.node_area

        self.from_param: "ParameterInterface" = from_param
        self.from_param_id: int = self.from_param.id
        self.from_node: "Node" = self.from_param.node
        self.from_node_id: int = self.from_node.id
        self.from_point: "ParameterConnectPoint" = self.from_param.connect_point

        self.path_color: str = self.from_point.point_color

        self.to_param: "ParameterInterface" = to_param
        self.to_param_id: int = self.to_param.id
        self.to_node: "Node" = self.to_param.node
        self.to_node_id: int = self.to_node.id
        self.to_point: "ParameterConnectPoint" = self.to_param.connect_point

        self.connect_path: cv.Path = self.create_connect_path()


    def __hash__(self) -> int:
        return hash((
            self.from_node_id, self.from_param_id,
            self.to_node_id, self.to_param_id
        ))
    

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, NodeConnection)
            and hash(self) == hash(other)
        )
    

    def __str__(self) -> str:
        return f"{self.from_node_id}:{self.from_param_id} -> {self.to_node_id}:{self.to_param_id}"
        # return f"{{from_node_id: {self.from_node_id}, from_param_id: {self.from_param_id}, to_node_id: {self.to_node_id}, to_param_id: {self.to_param_id}}}"
    

    def create_connect_path(self) -> cv.Path:
        '''
        Создает путь соединения
        '''
        self.path_paint = Paint(
            stroke_width = 2,
            style = PaintingStyle.STROKE,
            color = self.path_color
        )
        return cv.Path(
            elements = self.create_path_elements(),
            paint = self.path_paint,
        )
    

    def create_path_elements(self) -> List:
        '''
        Создает элементы пути соединения
        '''
        from_left, from_top = self.calculate_coord(self.from_point)
        to_left, to_top = self.calculate_coord(self.to_point)

        self.path_from_point = cv.Path.MoveTo(
            x = from_left,
            y = from_top
        )
        self.path_from_indent = cv.Path.LineTo(
            x = from_left + self.LINE_LEN,
            y = from_top
        )
        self.path_to_indent = cv.Path.CubicTo(
            cp1x = from_left + self.STEEPNESS,
            cp1y = from_top,
            cp2x = to_left - self.STEEPNESS,
            cp2y = to_top,
            x = to_left - self.LINE_LEN,
            y = to_top,
        )
        self.path_to_point = cv.Path.LineTo(
            x = to_left,
            y = to_top
        )
        return [
            self.path_from_point, self.path_from_indent,
            self.path_to_indent, self.path_to_point
        ]
    

    def calculate_coord(self, point: "ParameterConnectPoint") -> Tuple[int, int]:
        """
        Рассчитывает координаты точки
        """
        node: "Node" = point.node

        left_center = node.width // 2
        top_center = node.height // 2

        point_left = point.left + node.POINT_SIZE // 2 - left_center
        point_top = point.top + node.POINT_SIZE // 2 - top_center

        point_left_scl = point_left * self.node_area.current_scale + left_center
        point_top_scl = point_top * self.node_area.current_scale + top_center

        return node.left + point_left_scl, node.top + point_top_scl
    

    def update_connect_path(self) -> None:
        '''
        Обновляет путь соединения
        '''
        self.update_connect_path_from_param()
        self.update_connect_path_to_param()


    def update_connect_path_from_param(self) -> None:
        '''
        Обновляет путь соединения от источника параметра
        '''
        from_left, from_top = self.calculate_coord(self.from_point)
        self.set_update_connect_path_from_param(from_left, from_top)


    def set_update_connect_path_from_param(self, from_left: int, from_top: int) -> None:
        '''
        Устанавливает путь соединения от источника параметра
        '''
        self.path_from_point.x = from_left
        self.path_from_point.y = from_top

        self.path_from_indent.x = from_left + self.LINE_LEN
        self.path_from_indent.y = from_top

        self.path_to_indent.cp1x = from_left + self.STEEPNESS
        self.path_to_indent.cp1y = from_top


    def update_connect_path_to_param(self) -> None:
        '''
        Обновляет путь соединения к принимающему параметру
        '''
        to_left, to_top = self.calculate_coord(self.to_point)
        self.set_update_connect_path_to_param(to_left, to_top)
    

    def set_update_connect_path_to_param(self, to_left: int, to_top: int) -> None:
        '''
        Устанавливает путь соединения к принимающему параметру
        '''
        self.path_to_indent.cp2x = to_left - self.STEEPNESS
        self.path_to_indent.cp2y = to_top
        self.path_to_indent.x = to_left - self.LINE_LEN
        self.path_to_indent.y = to_top

        self.path_to_point.x = to_left
        self.path_to_point.y = to_top


    def change_from_param(self, from_param: "ParameterInterface") -> None:
        """
        Изменяет источник параметра
        """
        self.from_node.remove_connect_to(self.from_param, self.to_param)
        self.to_node.remove_connect_from(self.to_param)

        self.from_param: "ParameterInterface" = from_param
        self.from_param_id: int = self.from_param.id
        self.from_node: "Node" = self.from_param.node
        self.from_node_id: int = self.from_node.id
        self.from_point: "ParameterConnectPoint" = self.from_param.connect_point
        self.path_color: str = self.from_point.point_color
        self.path_paint.color = self.path_color

        self.from_node.add_connect_to(self.from_param, self.to_param)
        self.to_node.add_connect_from(self.from_param, self.to_param)

        self.update_connect_path_from_param()
        self.connect_path.update()


    def change_to_param(self, to_param: "ParameterInterface") -> None:
        '''
        Изменяет принимающий параметр
        '''
        self.from_node.remove_connect_to(self.from_param, self.to_param)
        self.to_node.remove_connect_from(self.to_param)

        self.to_param: "ParameterInterface" = to_param
        self.to_param_id: int = self.to_param.id
        self.to_node: "Node" = self.to_param.node
        self.to_node_id: int = self.to_node.id
        self.to_point: "ParameterConnectPoint" = self.to_param.connect_point

        self.from_node.add_connect_to(self.from_param, self.to_param)
        self.to_node.add_connect_from(self.from_param, self.to_param)

        self.update_connect_path_to_param()
        self.connect_path.update()


    def drag_connect_path(self, delta_x: int, delta_y: int) -> None:
        '''
        Перемещает путь соединения
        '''
        self.path_from_point.x += delta_x
        self.path_from_point.y += delta_y

        self.path_from_indent.x += delta_x
        self.path_from_indent.y += delta_y

        self.path_to_indent.cp1x += delta_x
        self.path_to_indent.cp1y += delta_y
        self.path_to_indent.cp2x += delta_x
        self.path_to_indent.cp2y += delta_y
        self.path_to_indent.x += delta_x
        self.path_to_indent.y += delta_y

        self.path_to_point.x += delta_x
        self.path_to_point.y += delta_y
