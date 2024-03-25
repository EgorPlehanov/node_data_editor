from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node_area.node_area import NodeArea
    from ..parameters import ParameterInterface
    from .node_connection import NodeConnection

from .node_config import NodeConfig
from ..calculation_functions import NodeResult
from ..result_area import ResultView
from .node_view import NodeView

from flet import *
from itertools import count
from typing import List, Dict, Any, get_type_hints
from inspect import signature
import keyboard



class Node(GestureDetector):
    """
    Карточка узла (нода)
    """

    id_counter = count()

    def __init__(
        self,
        page: Page,
        node_area: "NodeArea",
        scale = 1,
        config: NodeConfig = NodeConfig()
    ):
        super().__init__()
        self.page = page
        self.node_area = node_area
        self.result_area = self.node_area.workplace.result_area
        self.config = config

        self.scale = scale

        self.setup_values()
        
        self.node_view: NodeView = NodeView(
            node = self,
            config = self.config
        )
        self.content = self.node_view
        self.parameters_dict = self.node_view.parameters_dict
        self.height = self.content.get_height()

        self.calculate(is_init=True)


    def __str__(self) -> str:
        return f"Node: id: {self.id}, name: {self.name}"
    

    def __hash__(self) -> int:
        return hash(self.id)


    def __eq__(self, other):
        return isinstance(other, Node) and hash(self) == hash(other)


    def setup_values(self) -> None:
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
        self.is_processing = False
        self.is_display_result = self.config.is_display_result

        self.name = self.config.name

        self.left = self.config.left
        self.top = self.config.top

        self.width = self.config.width

        self.function = self.config.function
        self.function_signature = self.get_signature_type_hints()

        self.parameters_results_view_dict: Dict = {
            param.key: None
            for param in self.config.parameters
        }


    def delete(self, e) -> None:
        """
        Удаляет узел
        """
        self.node_area.delete_node(self)
    

    def on_drag_start(self, e: DragStartEvent) -> None:
        """
        Обработка начала перемещения узла
        """
        if keyboard.is_pressed('ctrl'):
            self.toggle_selection()
        elif not self.is_selected:
            self.node_area.clear_selection()
            self.set_selection_value(True)
    

    def on_drag(self, e: DragUpdateEvent) -> None:
        """
        Обработка перемещения узла
        """
        if not keyboard.is_pressed('ctrl'):
            self.node_area.drag_selection(top_delta = e.delta_y, left_delta = e.delta_x)


    def drag_node(self, left_delta = 0, top_delta = 0) -> None:
        """
        Переместить узел
        """
        self.top = max(0, self.top + top_delta * self.scale)
        self.left = max(0, self.left + left_delta * self.scale)


    def on_tap_select(self, e: TapEvent) -> None:
        """
        Обработка нажатия на узел
        """
        if keyboard.is_pressed('ctrl'):
            self.toggle_selection()
        else:
            self.node_area.clear_selection()
            self.set_selection_value(True)


    def set_selection_value(self, is_selected: bool) -> None:
        """
        Выделить узел
        """
        if self.is_selected == is_selected:
            return
        self.is_selected = is_selected
        self.node_view.set_selection_style()
        self.update()


    def set_processing_state(self, is_processing: bool, is_init: bool = False) -> None:
        """
        Устанавливает состояние обработки узла
        """
        self.is_processing = is_processing
        if not is_init:
            self.node_view.set_progress_bar_state(is_processing)


    def toggle_selection(self, is_update = True) -> None:
        """
        Переключает выделение узла
        """
        self.is_selected = not self.is_selected
        self.node_view.set_selection_style()
        if is_update:
            self.update()


    def calculate(
        self,
        is_recalculate_dependent_nodes: bool = True,
        is_init: bool = False
    ) -> None:
        '''
        Вычисляет значение функции
        '''
        self.set_processing_state(is_processing = True, is_init = is_init)

        try:
            valid_parameters = self._get_valid_parameters()
            self.result: Dict = self.function(**valid_parameters)
        except Exception as e:
            self.result = {"error": str(e)}
        self.set_result_to_out_parameters()
        print(self.id, self.name, self.result) # ОТЛАДКА TEST

        if self.is_display_result:
            self.display_result()

        self.set_processing_state(is_processing = False, is_init = is_init)

        if is_recalculate_dependent_nodes:
            self.node_area.recalculate_dependent_nodes(self)


    def set_result_to_out_parameters(self) -> None:
        '''
        Устанавливает значение выходного параметра
        '''
        common_keys = [key for key in self.result.keys() if key in self.parameters_dict.keys()]
        for res_param in common_keys:
            self.parameters_dict[res_param].value = self.result[res_param]


    def get_signature_type_hints(self) -> dict:
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
        valid_parameters = {}
        for name in self.function_signature:
            value = self.parameters_dict[name].value

            if self.parameters_dict[name].is_connected:
                connect: "NodeConnection" = self.parameters_dict[name].connect_point.current_connect
                
                if connect is None:
                    value = self.parameters_dict[name].value
                else:
                    value = connect.from_param.value

            if self.is_valid_parameter(name, value):
                valid_parameters[name] = self.get_parameter_value(value)
        
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
    

    def display_result(self) -> None:
        '''
        Отображает значение выходного параметра
        '''
        for param_key, result in self.result.items():
            if param_key not in self.parameters_results_view_dict:
                continue
            
            result_control: ResultView = self.parameters_results_view_dict[param_key]

            connect: "NodeConnection" = self.parameters_dict[param_key].connect_point.current_connect

            if result["label"] == "" and connect is not None:
                result["label"] = connect.from_node.name

            if result_control is None:
                result_control = ResultView(self, self.result_area, result)
                self.result_area.add_node_results(result_control)
                self.parameters_results_view_dict[param_key] = result_control
            else:
                result_control.update_result(result)
                
        self.result_area.update()
        