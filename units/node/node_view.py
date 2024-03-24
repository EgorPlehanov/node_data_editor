from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node import Node
    from ..parameters import ParameterInterface
    from ..parameters.parameter_typing.parameter_connect_point import ParameterConnectPoint
    from .node_config import NodeConfig

from ..data_types import ParameterConnectType
from ..parameters import type_to_param

from flet import *
from typing import List, Dict
import math



class NodeView(Stack):

    HEADER_HEIGHT = 30
    BORDER_RADIUS = HEADER_HEIGHT // 2
    BORDER_WIDTH = 1

    POINT_SIZE = 12
    POINT_BORDER_WIDTH = 1

    CONTENT_MARGIN = POINT_SIZE // 2
    PARAM_PADDING = 5

    NODE_BGCOLOR = colors.with_opacity(0.90, colors.GREY_900)
    NODE_BORDER_COLOR = colors.BLACK87
    NODE_SELECT_BGCOLOR = colors.GREY_800
    NODE_SELECT_BORDER_COLOR = colors.DEEP_ORANGE_ACCENT_400
    NODE_SHADOW_COLOR = colors.BLACK38

    HEADER_ICON_COLOR = colors.WHITE
    HEADER_SHADOW_COLOR = colors.BLACK26

    def __init__(
        self,
        node: 'Node',
        config: 'NodeConfig',
    ):
        super().__init__()
        self.node = node
        self.config = config

        self.set_style()

        self.header: Container = self.create_header()
        self.parameters: Container = self.create_parameters()
        self.connect_points: List["ParameterConnectPoint"] = self.create_contact_points_list()

        self.controls = self.create_controls()

        self.height = self.get_height()


    def set_style(self):
        """
        Устанавливает стиль узла
        """
        self.clip_behavior = ClipBehavior.NONE

        self.header_color = self.config.color


    def create_controls(self):
        """
        Создает карточку узла
        """
        self.ref_content_conteiner = Ref[Container]()
        return [
            Container(
                ref = self.ref_content_conteiner,
                content = Column(
                    controls = [
                        self.header,
                        self.parameters
                    ],
                    spacing = 0,
                ),
                width = self.get_width_content(),
                left = self.CONTENT_MARGIN,
                top = self.CONTENT_MARGIN,
                visible = self.node.is_open,
                bgcolor = self.NODE_BGCOLOR,
                border_radius = border_radius.all(self.BORDER_RADIUS),
                border = border.all(self.BORDER_WIDTH, self.NODE_BORDER_COLOR),
                shadow = BoxShadow(
                    spread_radius = 0,
                    blur_radius = 5,
                    color = self.NODE_SHADOW_COLOR,
                    offset = Offset(0, 5),
                    blur_style = ShadowBlurStyle.NORMAL,
                ),
                # on_click = self.node.on_tap_select
            ),
            *self.connect_points
        ]
    

    def get_width_content(self) -> int:
        """
        Возвращает ширину контента карточки узла
        """
        return self.node.width - self.POINT_SIZE
    

    def create_header(self) -> Container:
        """
        Создает шапку узла
        """
        self.ref_collapse_button = Ref[IconButton]()
        collapse_button = IconButton(
            ref = self.ref_collapse_button,
            icon = icons.KEYBOARD_ARROW_DOWN,
            icon_color = self.HEADER_ICON_COLOR,
            on_click = self.toggle_parameters,
            icon_size = 15,
        )
        name_text = Text(
            value = f'{self.node.id}: {self.node.name}',
            expand = True,
            tooltip = self.node.name,
            max_lines = 1,
            text_align = TextAlign.CENTER,
        )
        delete_button = IconButton(
            icon = icons.CLOSE,
            icon_color = self.HEADER_ICON_COLOR,
            on_click = self.node.delete,
            icon_size = 15,
        )
        return Container(
            height = self.HEADER_HEIGHT,
            content = Row(
                controls = [
                    collapse_button,
                    name_text,
                    delete_button
                ],
                alignment = MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor = colors.with_opacity(0.5, self.header_color),
            border_radius = border_radius.only(
                top_left = self.BORDER_RADIUS, top_right = self.BORDER_RADIUS
            ),
            shadow = BoxShadow(
                spread_radius = 0,
                blur_radius = 5,
                color = self.HEADER_SHADOW_COLOR,
                offset = Offset(0, 3),
                blur_style = ShadowBlurStyle.NORMAL,
            ),
        )


    def toggle_parameters(self, e) -> None:
        """
        Открывает/закрывает параметры узла
        """
        self.node.is_open = not self.node.is_open
        self.parameters.visible = self.node.is_open
        self.ref_collapse_button.current.icon = (
            icons.KEYBOARD_ARROW_DOWN
            if self.node.is_open
            else icons.KEYBOARD_ARROW_RIGHT
        )
        self.header.border_radius = (
            border_radius.only(top_left = self.BORDER_RADIUS, top_right = self.BORDER_RADIUS)
            if self.node.is_open
            else border_radius.all(self.BORDER_RADIUS)
        )
        for point in self.connect_points:
            if self.node.is_open:
                point.top, point.left = point.open_top, point.open_left
            else:
                point.top, point.left = point.close_top, point.close_left
        self.node.height = self.get_height()

        self.node.node_area.canvas_connections.update_connects_lines()
        self.node.update()


    def get_height(self) -> int:
        """
        Возвращает высоту карточки узла
        """
        if self.node.is_open:
            return self.get_height_content() + self.POINT_SIZE * 1.5
        else:
            return self.HEADER_HEIGHT + self.POINT_SIZE
            
    
    def get_height_content(self) -> int:
        """
        Возвращает высоту контента карточки узла
        """
        return self.HEADER_HEIGHT + self.PARAM_PADDING * 2 + self.get_height_parameters()


    def get_height_parameters(self) -> int:
        """
        Возвращает высоту параметров
        """
        return sum(param.height for param in self.parameters_dict.values())


    def create_parameters(self) -> Container:
        """
        Создает параметры узла
        """
        self.parameters_dict: Dict[str, "ParameterInterface"] = self.create_parameters_dict(self.config.parameters)
        self.set_connect_points_coordinates()

        return Container(
            width = self.node.width,
            content = Column(
                controls = self.parameters_dict.values(),
                spacing = 0,
            ),
            padding = padding.all(self.PARAM_PADDING),
        )
    

    def create_parameters_dict(self, config_list: List["ParameterInterface"]) -> Dict:
        '''
        Создает список параметров
        '''
        return {
            config.key: type_to_param[config.type](node=self.node, config=config)
            for config in config_list
        }
    

    def set_connect_points_coordinates(self) -> None:
        """
        Устанавливает координаты точек связи
        """
        out_value_count = self.get_config_parameters_count_by_connect_type(ParameterConnectType.OUT)
        in_param_count = self.get_config_parameters_count_by_connect_type(ParameterConnectType.IN)

        out_center_x = self.node.width - self.POINT_SIZE // 2 - self.BORDER_RADIUS
        in_center_x = self.POINT_SIZE // 2 + self.BORDER_RADIUS
        center_y = self.HEADER_HEIGHT // 2

        out_close_coord = self.get_points_close_coordinates(
            center_x    = out_center_x,
            center_y    = center_y,
            radius      = self.BORDER_RADIUS,
            num_objects = out_value_count,
            angle_start = -90,
            angle_end   = 90,
        )
        in_close_coord  = self.get_points_close_coordinates(
            center_x    = in_center_x,
            center_y    = center_y,
            radius      = self.BORDER_RADIUS,
            num_objects = in_param_count,
            angle_start = -90,
            angle_end   = -270,
        )

        top = self.HEADER_HEIGHT + self.POINT_SIZE // 2 + self.PARAM_PADDING
        left_out = self.node.width - self.POINT_SIZE

        for param in self.parameters_dict.values():
            if param.has_connect_point:
                if param._connect_type == ParameterConnectType.OUT:
                    left = left_out
                    cords = out_close_coord.pop(0)
                else:
                    left = 0
                    cords = in_close_coord.pop(0)

                close_top = cords[1]
                close_left = cords[0] - self.POINT_SIZE // 2

                param.set_connect_point_coordinates(
                    open_top   = top + self.POINT_SIZE // 2,
                    open_left  = left,
                    close_top  = close_top,
                    close_left = close_left
                )
            top += param.height


    def get_config_parameters_count_by_connect_type(self, param_type: ParameterConnectType) -> int:
        """
        Возвращает количество параметров в конфигурации по типу связи
        """
        params_count = 0
        for param in self.config.parameters:
            if param.connect_type == param_type and param.has_connect_point:
                params_count += 1
        return params_count
    

    def get_points_close_coordinates(
        self,
        center_x, center_y,
        radius,
        num_objects,
        angle_start = 0,
        angle_end = 360,
        point_idx = None
    ) -> list:
        """
        Возвращает координаты точек контакта с окружностью
        (0 градусов справа на оси X, по часовой)

        center_x, center_y - координаты центра окружности
        radius - радиус окружности
        num_objects - количество точек
        angle_start - начальный угол
        angle_end - конечный угол
        point_idx - индекс точки, если None, то возвращает координаты всех точек
        """
        if num_objects < 1:
            return []
        step_angle = (angle_end - angle_start) / num_objects
        points = [
            (
                center_x + radius * math.cos(math.radians(angle_start + idx * step_angle + step_angle / 2)),
                center_y + radius * math.sin(math.radians(angle_start + idx * step_angle + step_angle / 2))
            )
            for idx in range(num_objects)
        ]
        return points if point_idx is None else points[point_idx]
    

    def create_contact_points_list(self) -> list:
        """
        Создает список точек контакта
        """
        return [
            param.connect_point for param in self.parameters_dict.values()
            if param.has_connect_point or param.connect_point is not None
        ]
    

    def set_selection_style(self) -> None:
        """
        Включает выделение узла
        """
        conteiner: Container = self.ref_content_conteiner.current
        if self.node.is_selected:
            conteiner.bgcolor = self.NODE_SELECT_BGCOLOR
            conteiner.border = border.all(self.BORDER_WIDTH, self.NODE_SELECT_BORDER_COLOR)
            self.node.node_area.add_selection_node(self.node)
        else:
            conteiner.bgcolor = self.NODE_BGCOLOR
            conteiner.border = border.all(self.BORDER_WIDTH, self.NODE_BORDER_COLOR)
            self.node.node_area.remove_selection_node(self.node)
    