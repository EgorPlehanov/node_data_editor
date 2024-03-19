from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node import Node

from flet import *
from enum import Enum
from typing import Any

    

class ParameterConnectType(Enum):
    '''
    Типы подключения

    IN - входной
    OUT - выходной
    '''
    IN = 'in'
    OUT = 'out'

    def __str__(self):
        return self.value



class NodeConnectPoint(Container):
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
        connect_type: ParameterConnectType = ParameterConnectType.OUT,
        color: str = colors.GREY_500,
        size: int = 12,
    ):
        super().__init__()
        self.node = node
        self.parameter = parameter

        self.node_id = self.node.id
        self.id = id
        
        self.connect_type = connect_type
        self.point_color = color
        self.point_current_color = color
        self.point_size = size

        self.top = top
        self.left = left

        self.open_top = top
        self.open_left = left
        self.close_top = close_top
        self.close_left = close_left

        self.point: Container = self.create_point()
        self.content = self.create_content()
        
        
    def create_point(self) -> Container:
        """
        Создает контакт
        """
        return Container(
            on_long_press = (
                lambda e: self.remove_node_from_connects_to()
                if self.connect_type == ParameterConnectType.IN else None
            ),
            bgcolor = self.point_current_color,
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
            ),
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
                data = {
                    'node_id': self.node_id,
                    'value_idx': self.id,
                    'color': self.point_color,
                    'type': 'out',
                },
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
    

    def drag_leave(self, e: ControlEvent):
        """
        Отменяент изменения drag_will_accept(), когда курсор убирают с цели
        """
        point_color = self.point_color
        if isinstance(self.content, Draggable):
            # self.point_current_color = self.content.data.get('color')
            point_color = self.point_current_color
        
        self.set_point_color(point_color)
        self.update()


    def drag_accept(self, e: DragTargetAcceptEvent):
        """
        Принимает контакт
        """
        src = self.page.get_control(e.src_id)

        src_type = src.data.get('type')
        src_node_id = src.data.get('node_id')
        src_value_idx = src.data.get('value_idx')
        src_color = src.data.get('color')
        src_cur_node_id = src.data.get('cur_node_id')
        src_cur_param_idx = src.data.get('cur_param_idx')
        if src_type == 'in':
            src_cur_param = self.node.node_area.get_node_parameter(src_cur_node_id, src_cur_param_idx)

        from_param = self.node.node_area.get_node_parameter(src_node_id, src_value_idx)

        # пропускаем связь с самим собой
        if src_node_id == self.node_id:
            self.drag_leave(e)
            return
        
        # удаляет связь при перетаскивании входного параметра из другого контакта
        if src_type == 'in':
            self.remove_node_from_connects_to(src_cur_param)

        if self.node.connects_from[self.parameter._key] is None:
            self.add_connects(from_param)
        elif from_param.id == self.node.connects_from[self.parameter._key].id:
            self.set_point_color(self.point_current_color, None)
            self.update()
            return
        else:
            self.remove_node_from_connects_to()
            self.add_connects(from_param)

            
        # Обновление цвета и данных Точки контакта
        data = src.data.copy()
        data['type'] = 'in'
        data['cur_node_id'] = self.node_id
        data['cur_param_idx'] = self.id

        if not isinstance(self.content, Draggable):
            self.content = Draggable(
                content = self.content,
                data = data
            )
        else:
            self.content.data = data
        self.set_point_color(src_color)
        self.point_current_color = src_color
            
        self.node.node_area.paint_line()
        self.parameter.set_connect_state(True)


    def set_point_color(self, point_color: str = None, border_color: str = colors.BLACK) -> None:
        """
        Устанавливает цвет Точки контакта
        """
        if point_color is None:
            point_color = self.point_color
        self.point.bgcolor = point_color
        self.point.border = border.all(self.POINT_BORDER_WIDTH, border_color)


    def add_connects(self, from_parameter):
        """
        Добавляет связь с текущим параметром
        """
        self.add_node_from_connects_to(from_parameter)
        self.add_coonects_from(from_parameter)


    def add_node_from_connects_to(self, from_parameter):
        """
        Добавляет ноде источника связь с текущем параметром
        """
        from_node: Node = from_parameter.node
        from_node.connects_to[from_parameter._key].append(self.parameter)
            

    def add_coonects_from(self, from_parameter):
        """
        Добавляет текущему параметру связь с нодой источника
        """
        self.node.connects_from[self.parameter._key] = from_parameter


    def remove_node_from_connects_to(self, to_parameter = None, recalculate_and_paint = True):
        """
        Удаляет ноде источника связь с текущем параметром
        """
        if to_parameter is None:
            to_parameter = self.parameter

        to_node = to_parameter.node

        from_parameter = to_node.connects_from[to_parameter._key]
        from_node: Node = from_parameter.node

        to_node.connects_from[to_parameter._key] = None
        to_parameter.set_connect_state(False, recalculate = recalculate_and_paint)

        to_point = to_parameter.connect_point
        to_point.point_current_color = to_point.point_color
        to_point.set_point_color()
        if isinstance(to_point.content, Draggable):
            to_point.content = to_point.content.content

        from_node.connects_to[from_parameter._key].remove(to_parameter)
        
        if recalculate_and_paint:
            from_node.node_area.paint_line()
