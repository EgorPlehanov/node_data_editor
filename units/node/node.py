from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node_area import NodeArea

from flet import *
from itertools import count
from typing import Callable, List, Dict, get_type_hints
from inspect import signature
from dataclasses import dataclass, field
import math
import keyboard

from .node_typing import Color
from ..parameters.parameters_dict import *
from .calculate_function.calculate_function_typing import *
from .node_result_view import *



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
    parameters: Dict | List = field(default_factory=list)
    is_display_result: bool = False
    
    
    def __post_init__(self):
        for attr in ("key", "name", "group"):
            value = getattr(self, attr)
            if not isinstance(value, str) or not value:
                try:
                    setattr(self, attr, str(value))
                except ValueError:
                    raise ValueError(f"Недопустимый тип {attr}: {type(value)}")



class Node(GestureDetector):
    id_counter = count()

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


    def __init__(self, page: Page, node_area: "NodeArea", scale = 1,
        config: NodeConfig = NodeConfig()
    ):
        super().__init__()
        self.page = page
        self.node_area = node_area
        self.config = config

        self.scale = scale

        self.setup_values()
        
        self.header = self.create_header()
        self.parameters = self.create_parameters()
        
        self.height = self.get_height()

        self.connect_points = self.create_contact_points_list()
        self.content = self.create_content()

        self.calculate()


    def setup_values(self):
        """
        Устанавливает значения по умолчанию
        """
        self.id = next(Node.id_counter)
        self.mouse_cursor = MouseCursor.CLICK
        self.drag_interval = 20
        self.on_pan_start = self.on_drag_start
        self.on_pan_update = self.on_drag
        self.on_tap = self.on_tap_select

        self.is_open = True
        self.is_selected = False
        self.is_display_result = self.config.is_display_result

        self.name = self.config.name

        self.left = self.config.left
        self.top = self.config.top

        self.width = self.config.width

        self.header_color = self.config.color

        self.function = self.config.function
        self.function_signature = self.get_signature_type_hints()

        self.connects_from: Dict[str, "ParamInterface"] = {
            param.key: None
            for param in self.config.parameters
        }
        self.connects_to: Dict[str, List["ParamInterface"]] = {
            param.key: []
            for param in self.config.parameters
        }

        self.parameters_results_view_dict: Dict = {
            param.key: None
            for param in self.config.parameters
        }


    def add_connect_to(self, param_from: ParamInterface, param_to: ParamInterface):
        """
        Добавляет связь из текущего параметра в зависимый параметр
        """
        self.connects_to[param_from._key].append(param_to)


    def add_connect_from(self, param_from: ParamInterface, param_to: ParamInterface):
        """
        Добавляет связь из параметра источника в параметр текущего узла
        """
        self.connects_from[param_to._key] = param_from


    def remove_connect_to(self, param_from: ParamInterface, param_to: ParamInterface):
        """
        Удаляет связь из текущего параметра в зависимый параметр
        """
        self.connects_to[param_from._key].remove(param_to)


    def remove_connect_from(self, param_to: ParamInterface):
        """
        Удаляет связь из параметра источника в параметр текущего узла
        """
        self.connects_from[param_to._key] = None


    def get_height(self):
        """
        Возвращает высоту карточки узла
        """
        if self.is_open:
            return self.get_height_content() + self.POINT_SIZE * 1.5
        else:
            return self.HEADER_HEIGHT + self.POINT_SIZE
            
    
    def get_height_content(self):
        """
        Возвращает высоту контента карточки узла
        """
        return self.HEADER_HEIGHT + self.PARAM_PADDING * 2 + self.get_height_parameters()


    def get_height_parameters(self):
        """
        Возвращает высоту параметров
        """
        return sum(param.height for param in self.parameters_dict.values())
    

    def get_width_content(self):
        """
        Возвращает ширину контента карточки узла
        """
        return self.width - self.POINT_SIZE
    

    def create_content(self):
        """
        Создает карточку узла
        """
        self.ref_content_conteiner = Ref[Container]()
        return Stack(
            [
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
                    visible = self.is_open,
                    bgcolor = self.NODE_BGCOLOR,
                    border_radius = border_radius.all(self.BORDER_RADIUS),
                    border = border.all(self.BORDER_WIDTH, self.NODE_BORDER_COLOR),
                    shadow = BoxShadow(
                        spread_radius = 0,
                        blur_radius = 5,
                        color = self.NODE_SHADOW_COLOR,
                        offset = Offset(0, 5),
                        blur_style = ShadowBlurStyle.NORMAL,
                    )
                ),
                *self.connect_points
            ], clip_behavior=ClipBehavior.NONE
        )
    

    def create_header(self):
        """
        Создает шапку узла
        """
        self.ref_open_button = Ref[IconButton]()
        return Container(
            height = self.HEADER_HEIGHT,
            content = Row(
                controls = [
                    IconButton(
                        ref = self.ref_open_button,
                        icon = icons.KEYBOARD_ARROW_DOWN,
                        icon_color = self.HEADER_ICON_COLOR,
                        on_click = self.toggle_parameters,
                        icon_size = 15,
                    ),
                    Text(
                        value = f'{self.id}: {self.name}',
                        expand = True,
                        tooltip = self.name,
                        max_lines = 1,
                        text_align = TextAlign.CENTER,
                    ),
                    IconButton(
                        icon = icons.CLOSE,
                        icon_color = self.HEADER_ICON_COLOR,
                        on_click = self.delete,
                        icon_size = 15,
                    )
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


    def toggle_parameters(self, e):
        """
        Открывает/закрывает параметры узла
        """
        self.is_open = not self.is_open
        self.parameters.visible = self.is_open
        self.ref_open_button.current.icon = (
            icons.KEYBOARD_ARROW_DOWN
            if self.is_open
            else icons.KEYBOARD_ARROW_RIGHT
        )
        self.header.border_radius = (
            border_radius.only(top_left = self.BORDER_RADIUS, top_right = self.BORDER_RADIUS)
            if self.is_open
            else border_radius.all(self.BORDER_RADIUS)
        )
        for point in self.connect_points:
            if self.is_open:
                point.top, point.left = point.open_top, point.open_left
            else:
                point.top, point.left = point.close_top, point.close_left
        self.height = self.get_height()

        self.node_area.paint_line()
        self.content.update()
    

    def delete(self, e):
        """
        Удаляет узел
        """
        self.node_area.delete_node(self)
    

    def create_parameters(self):
        """
        Создает параметры узла
        """
        self.parameters_dict: Dict = self.create_parameters_dict(self.config.parameters)
        self.set_connect_points_coordinates()

        return Container(
            width = self.width,
            content = Column(
                controls = self.parameters_dict.values(),
                spacing = 0,
            ),
            padding = padding.all(self.PARAM_PADDING),
        )
    

    def create_parameters_dict(self, config_list: list) -> Dict:
        '''
        Создает список параметров
        '''
        return {
            config.key: type_to_param[config.type](node=self, config=config)
            for config in config_list
        }
    

    def set_connect_points_coordinates(self):
        """
        Устанавливает координаты точек связи
        """
        
        out_value_count = len([
            param for param in self.config.parameters
            if param.connect_type == ParameterConnectType.OUT and param.has_connect_point
        ])
        in_param_count = len([
            param for param in self.config.parameters
            if param.connect_type == ParameterConnectType.IN and param.has_connect_point
        ])

        out_center_x = self.width - self.POINT_SIZE // 2 - self.BORDER_RADIUS
        in_center_x = self.POINT_SIZE // 2 + self.BORDER_RADIUS
        center_y = self.HEADER_HEIGHT // 2

        out_close_coord = self.get_points_close_coordinates(
            center_x = out_center_x,
            center_y = center_y,
            radius = self.BORDER_RADIUS,
            num_objects = out_value_count,
            angle_start = -90,
            angle_end = 90,
        )
        in_close_coord = self.get_points_close_coordinates(
            center_x = in_center_x,
            center_y = center_y,
            radius = self.BORDER_RADIUS,
            num_objects = in_param_count,
            angle_start = -90,
            angle_end = -270,
        )

        top = self.HEADER_HEIGHT + self.POINT_SIZE // 2 + self.PARAM_PADDING
        left_out = self.width - 12

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
                    open_top = top + self.POINT_SIZE // 2,
                    open_left = left,
                    close_top = close_top,
                    close_left = close_left
                )

            top += param.height
    

    def create_contact_points_list(self):
        """
        Создает точки контакта
        """
        return [
            param.connect_point for param in self.parameters_dict.values()
            if param.has_connect_point or param.connect_point is not None
        ]
    

    def get_points_close_coordinates(
        self,
        center_x, center_y,
        radius,
        num_objects,
        angle_start = 0,
        angle_end = 360,
        point_idx = None
    ):
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
    

    def on_drag_start(self, e: DragStartEvent):
        """
        Обработка начала перемещения узла
        """
        if keyboard.is_pressed('shift'):
            self.toggle_selection()
        elif not self.is_selected:
            self.node_area.clear_selection()
            self.set_selection_value(True)
    

    def on_drag(self, e: DragUpdateEvent):
        """
        Обработка перемещения узла
        """
        if not keyboard.is_pressed('shift'):
            self.node_area.drag_selection(top_delta = e.delta_y, left_delta = e.delta_x)


    def drag_node(self, left_delta = 0, top_delta = 0):
        """
        Переместить узел
        """
        self.top = max(0, self.top + top_delta * self.scale)
        self.left = max(0, self.left + left_delta * self.scale)


    def on_tap_select(self, e: TapEvent):
        """
        Обработка нажатия на узел
        """
        if keyboard.is_pressed('shift'):
            self.toggle_selection()
        else:
            self.node_area.clear_selection()
            self.set_selection_value(True)
            


    def set_selection_value(self, is_selected: bool):
        """
        Выделить узел
        """
        if self.is_selected == is_selected:
            return
        self.is_selected = is_selected
        self.set_selection_style()
        self.update()


    def toggle_selection(self, is_update = True):
        """
        Переключает выделение узла
        """
        self.is_selected = not self.is_selected
        self.set_selection_style()
        if is_update:
            self.update()


    def set_selection_style(self):
        """
        Включает выделение узла
        """
        conteiner: Container = self.ref_content_conteiner.current
        if self.is_selected:
            conteiner.bgcolor = self.NODE_SELECT_BGCOLOR
            conteiner.border = border.all(self.BORDER_WIDTH, self.NODE_SELECT_BORDER_COLOR)
            self.node_area.add_selection_node(self)
        else:
            conteiner.bgcolor = self.NODE_BGCOLOR
            conteiner.border = border.all(self.BORDER_WIDTH, self.NODE_BORDER_COLOR)
            self.node_area.remove_selection_node(self)


    def calculate(self):
        '''
        Вычисляет значение функции
        '''
        try:
            valid_parameters = self._get_valid_parameters()
            self.result: Dict = self.function(**valid_parameters)
        except Exception as e:
            self.result = {"error": str(e)}
        self.set_result_to_out_parameters()
        print(self.id, self.name, self.result) # ОТЛАДКА TEST
        self.recalculate_connects_to_node()
        if self.is_display_result:
            self.display_result()
        

    def set_result_to_out_parameters(self):
        '''
        Устанавливает значение выходного параметра
        '''
        common_keys = [key for key in self.result.keys() if key in self.parameters_dict.keys()]
        for res_param in common_keys:
            self.parameters_dict[res_param].value = self.result[res_param]


    def recalculate_connects_to_node(self):
        """
        Запускает пересчет значений зависимых нод
        """
        node_to_recalculate = set(
            to_param.node
            for to_param_list in self.connects_to.values() 
            for to_param in to_param_list
        )
        for node in node_to_recalculate:
            node.calculate()


    def get_signature_type_hints(self):
        '''
        Возвращает типы параметров функции
        '''
        if self.function is None:
            return {}
        type_hints = get_type_hints(self.function)
        type_hints.pop('return', None)
        return {
            name: type_hints.get(name)
            for name in signature(self.function).parameters
        }
    

    def _get_valid_parameters(self) -> dict:
        '''Возвращает текущие значения параметров функции с учетом сигнатуры функции'''
        valid_parameters = {
            name: self.get_parameter_value(
                self.parameters_dict[name].value
                if not self.parameters_dict[name].is_connected
                else self.connects_from[name].value
            )
            for name in self.function_signature
            if self.is_valid_parameter(
                name,
                self.get_parameter_value(
                    self.parameters_dict[name].value
                    if not self.parameters_dict[name].is_connected
                    else self.connects_from[name].value
                )
            )
        }
        if len(valid_parameters) != len(self.function_signature):
            raise ValueError(
                "Количество параметров не совпадает, "
                + f"ожидалось {len(self.function_signature)} и получено {len(valid_parameters)}\n"
                + f"\nПараметры: {self.function_signature}"
                + f"\nВалидные: {valid_parameters}"
            )
        return valid_parameters
    

    def get_parameter_value(self, value: Any) -> Any:
        '''
        Возвращает значение параметра
        '''
        if isinstance(value, NodeResult) and not self.is_display_result:
            return value.value
        return value
    

    def is_valid_parameter(self, name: str, value) -> bool:
        '''
        Возвращает True, если параметр имеет допустимый тип
        '''
        if (
            (
                self.function_signature[name] in [bool, int, str]
                and not type(value) == self.function_signature[name]
            ) or (
                self.function_signature[name] in [float]
                and not isinstance(value, (float, int))
            )
        ):
            raise TypeError(f"Тип параметра {name} должен быть типа {self.function_signature[name]}, а не {type(value)}")
        return True
    

    def display_result(self):
        '''
        Отображает значение выходного параметра
        '''
        result_area = self.node_area.workplace.result_area
        for param_key, result in self.result.items():
            if param_key not in self.parameters_results_view_dict:
                continue

            result_control: NodeResultView = self.parameters_results_view_dict[param_key]
            if result["label"] == "" and self.connects_from[param_key] is not None:
                result["label"] = self.connects_from[param_key].node.name
            if result_control is None:
                result_control = NodeResultView(self, result_area, result)
                result_area.result_controls.insert(0, result_control)
                self.parameters_results_view_dict[param_key] = result_control
            else:
                result_control.update_result(result)
                
        result_area.update()


    def __str__(self):
        return f"Node: id: {self.id}, name: {self.name}"