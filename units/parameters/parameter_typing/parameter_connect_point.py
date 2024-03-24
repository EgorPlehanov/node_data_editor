from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...node.node import Node
    from .. import ParameterInterface

from ...data_types import ParameterConnectType
from ...node.node_connection import NodeConnection

from flet import *
from typing import Any, Union



class ParameterConnectPoint(Container):
    """
    Класс для отрисовки точки контакта нод
    Используется для подключения параметров
    """

    POINT_BORDER_WIDTH = 1

    def __init__(
        self,
        node: "Node",
        parameter: Any,
        id: int,
        top: int = 0,
        left: int = 0,
        close_top: int = 0,
        close_left: int = 0,
        connect_type: "ParameterConnectType" = ParameterConnectType.OUT,
        color: str = colors.GREY_500,
        size: int = 12,
    ):
        super().__init__()
        self.node = node
        self.node_area_connections = self.node.node_area.canvas_connections
        self.parameter: "ParameterInterface" = parameter

        self.node_id = self.node.id
        self.id = id
        
        self.connect_type = connect_type
        self.point_color = color
        self.point_size = size
        
        self.current_point_color = color
        self.current_connect = None

        self.top = top
        self.left = left

        self.open_top = top
        self.open_left = left
        self.close_top = close_top
        self.close_left = close_left

        self.point: Container = self.create_point()
        self.content: Union[DragTarget, Draggable] = self.create_content()

    
    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ParameterConnectPoint)
            and self.id == other.id
        )
    

    def __hash__(self) -> int:
        return hash((self.id, self.node_id))
        
        
    def create_point(self) -> Container:
        """
        Создает точку контакта
        """
        return Container(
            on_long_press = lambda e: self.clear_connect(),
            bgcolor = self.current_point_color,
            width = self.point_size,
            height = self.point_size,
            shape = BoxShape.CIRCLE,
            border = border.all(self.POINT_BORDER_WIDTH, colors.BLACK),
            shadow = BoxShadow(
                spread_radius = 0,
                blur_radius = 5,
                color = colors.BLACK38,
                offset = Offset(0, 5),
                blur_style = ShadowBlurStyle.NORMAL,
            )
        )


    def create_content(self) -> DragTarget | Draggable:
        """
        Создает контент контакта
        """
        if self.connect_type == ParameterConnectType.IN:
            return DragTarget(
                content = self.point,
                on_will_accept = self.drag_will_accept,
                on_accept = self.drag_accept,
                on_leave = self.drag_leave
            )
        else:
            return Draggable(
                data = self,
                content = self.point,
            )
    

    def drag_will_accept(self, e: ControlEvent) -> None:
        """
        Показывает может ли узел принять контакт
        """
        self.point.border = border.all(
            self.POINT_BORDER_WIDTH,
            colors.GREEN if e.data == "true" else colors.RED
        )
        self.point.bgcolor = (colors.GREEN if e.data == "true" else colors.RED)
        self.update()
    

    def drag_leave(self, e: ControlEvent) -> None:
        """
        Отменяент изменения drag_will_accept(), когда курсор убирают с цели
        """
        self.set_point_color(
            point_color = (
                self.current_point_color
                if self.parameter.is_connected
                else self.point_color
            ),
            is_update = True
        )


    def drag_accept(self, e: DragTargetAcceptEvent) -> None:
        """
        Принимает контакт
        """
        src_data: Union[NodeConnection, ParameterConnectPoint] = self.page.get_control(e.src_id).data
        
        if isinstance(src_data, ParameterConnectPoint):
            self.handle_node_connect_point_data(e, src_data)
            
        elif isinstance(src_data, NodeConnection):
            self.handle_node_connection_data(e, src_data)

        else:
            print("Неизвестный тип src_data")


    def handle_node_connect_point_data(self, e: DragTargetAcceptEvent, src_data: "ParameterConnectPoint") -> None:
        """
        Обрабатывает данные от выходного параметра (NodeConnectPoint)
        """
        if src_data.node == self.node:
            self.drag_leave(e)

        else:
            if self.parameter.is_connected:
                if src_data.parameter == self.current_connect.from_param:
                    self.drag_leave(e)

                else:
                    from_param: "ParameterInterface" = src_data.parameter
                    self.current_connect.change_from_param(from_param)
                    self.current_point_color = self.current_connect.path_color
                    self.set_point_color(
                        point_color = self.current_point_color,
                        is_update = True
                    )
                    self.node.calculate()
                    
            else:
                from_param: "ParameterInterface" = src_data.parameter
                connect = NodeConnection(
                    from_param = from_param,
                    to_param = self.parameter,
                )
                self.node_area_connections.add_node_connect(connect)
                self.set_current_connect(connect)

    
    def handle_node_connection_data(self, e: DragTargetAcceptEvent, src_data: NodeConnection) -> None:
        """
        Обрабатывает данные от подключения к другому параметру (NodeConnection)
        """
        if src_data.from_node == self.node or src_data == self.current_connect:
            self.drag_leave(e)

        else:
            if self.parameter.is_connected:
                self.node_area_connections.remove_node_connect(self.current_connect)

                cur_to_point: ParameterConnectPoint = src_data.to_point
                cur_to_point.clear_point_on_reconnect(
                    is_recalculate = self.current_connect.to_node != src_data.to_node
                )

                src_data.change_to_param(self.parameter)
                self.set_current_connect(src_data)

            else:
                cur_to_point: ParameterConnectPoint = src_data.to_point
                cur_to_point.clear_point_on_reconnect()

                src_data.change_to_param(self.parameter)
                self.set_current_connect(src_data)


    def set_current_connect(self, connect: NodeConnection) -> None:
        """
        Устанавливает текущее соединение
        """
        self.current_connect = connect
        self.current_point_color = connect.path_color
        self.make_draggable_on_connect(self.current_connect)
        self.parameter.set_connect_state(True)


    def clear_point_on_reconnect(self, is_recalculate: bool = True) -> None:
        """
        Очищает цвет контакта при переподключении из текущего параметра в другой
        """
        self.current_connect = None
        self.current_point_color = self.point_color
        self.content.content = self.point
        self.set_point_color(is_update=True)
        self.parameter.set_connect_state(
            is_connected = False,
            is_recalculate = is_recalculate
        )


    def make_draggable_on_connect(self, connect: NodeConnection) -> None:
        """
        Переводит контакт в состояние перетаскивания
        """
        self.content.content = Draggable(
            content = self.point,
            data = connect,
        )
        self.current_point_color = connect.path_color
        self.set_point_color(is_update=True)


    def set_point_color(self,
        point_color: str = None,
        border_color: str = colors.BLACK,
        is_update: bool = False
    ) -> None:
        """
        Устанавливает цвет Точки контакта
        """
        if point_color is None:
            point_color = (
                self.point_color
                if self.current_connect is None
                else self.current_point_color
            )
        self.point.bgcolor = point_color
        self.point.border = border.all(self.POINT_BORDER_WIDTH, border_color)
        if is_update:
            self.update()


    def clear_connect(self) -> None:
        """
        Удаляет соединеие
        """
        if self.parameter.is_connected:
            self.node_area_connections.remove_node_connect(self.current_connect)
            self.clear_point_on_reconnect()


    

    def on_point_drag(self, e: DragUpdateEvent) -> None:
        """
        Обработка перемещения контакта
        """
        # TODO: Придумать как сделать перемещение линии при подключении 
        print(type(e))
        print("global", e.global_x, e.global_y)