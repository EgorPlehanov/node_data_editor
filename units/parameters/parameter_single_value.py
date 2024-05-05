from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from .parameter_typing import *
from ..data_types import ParameterConnectType

from flet import *
from dataclasses import dataclass
import keyboard



@dataclass
class SingleValueParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра с одним значением

    default_value - значение параметра (по умолчанию)
    velue_step - шаг изменения значения
    min_value - минимальное значение
    max_value - максимальное значение
    """
    
    default_value: int | float = 0
    value_step: int | float = 1
    min_value: int | float = None
    max_value: int | float = None
    decimal_accuracy: int = None

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.SINGLE_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN



class SingleValueParam(Container, ParameterInterface):
    '''
    Параметр с одним значением
    '''

    def __init__(
        self,
        node: 'Node',
        config: SingleValueParamConfig = SingleValueParamConfig()
    ):
        self._type: ParameterType = ParameterType.SINGLE_VALUE
        self._connect_type: ParameterConnectType = ParameterConnectType.IN

        self.node = node
        self._config: SingleValueParamConfig = config
        
        super().__init__()
        self.__post_init__()

        self.set_style()
        
        self.main_control = self._create_main_control()
        self.enter_control = self._create_enter_control()
        self.connected_control = self._create_connected_control()

        self.content = self._create_content()

        if self._config.has_connect_point:
            self.connect_point = self._create_connect_point()



    def set_style(self) -> None:
        """
        Устанавливает стиль параметра
        """
        self.value_step = self._config.value_step
        self.min_value = self._config.min_value
        self.max_value = self._config.max_value
        self.decimal_accuracy = self._config.decimal_accuracy
        self.value = self.min_max_check(self._config.default_value)

        self.is_drag_changed = False

        self.margin = margin.only(left = 3, right = 3)
        self.padding = padding.only(top = self.PADDING_VERTICAL_SIZE, bottom = self.PADDING_VERTICAL_SIZE)
        self.border_radius = 5


    def _create_content(self) -> Column:
        '''
        Создает содержимое параметра
        '''
        return Column(
            controls = [
                self.main_control,
                self.enter_control,
                self.connected_control,
            ],
            spacing = 0
        )
        

    def _create_main_control(self) -> Container:
        '''
        Создает основное содержимое параметра
        '''
        self.ref_main_control_value = Ref[Text]()
        return Container(
            on_click = self._ckick_to_enter,
            on_hover = self._on_main_control_hover,
            visible = not self.is_connected,
            content = GestureDetector(
                content = Row(
                    controls = [
                        Text(self.name),
                        Text(
                            ref = self.ref_main_control_value,
                            value = self.value,
                        )
                    ],
                    alignment = MainAxisAlignment.SPACE_BETWEEN,
                ),
                on_horizontal_drag_start = self.drag_value_update_start,
                on_horizontal_drag_end = self.drag_value_update_end,
                on_horizontal_drag_update = self.drag_value_update,

            ),
            padding = padding.only(left = 5, right = 5),
            bgcolor = self.MAIN_COLOR
        )
    
    
    def _create_enter_control(self) -> Row:
        '''
        Создает поле ввода значения
        '''
        self.ref_enter_textfield = Ref[TextField]()
        return Row(
            visible = False,
            controls = [
                TextField(
                    ref = self.ref_enter_textfield,
                    keyboard_type = KeyboardType.NUMBER,
                    expand = True,
                    height = self.control_height,
                    value = str(self.value),
                    on_blur = self._on_enter_blur,
                    on_change = self._on_enter_change,
                    content_padding = padding.only(left = 5, right = 5),
                    focused_border_color = self.ACCENT_COLOR,
                    focused_border_width = 1,
                )
            ]
        )
    
    
    def _create_connected_control(self) -> Container:
        '''
        Создает содержимое параметра когда он подключен
        '''
        return Container(
            visible = self.is_connected,
            content = Row(
                controls = [
                    Text(self.name)
                ]
            ),
            padding = padding.only(left = 5, right = 5),
        )
    

    def _ckick_to_enter(self, e: ControlEvent) -> None:
        '''
        При клике на параметр открывает поле ввода
        '''
        self.main_control.visible = False
        self.enter_control.visible = True
        self.ref_enter_textfield.current.value = self.value
        self.ref_enter_textfield.current.focus()
        self.update()


    def _on_main_control_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на основное содержимое
        '''
        self.ref_main_control_value.current.color = self.ACCENT_COLOR if e.data == "true" or self.is_drag_changed else None
        e.control.bgcolor = self.HOVER_COLOR if e.data == "true" else self.MAIN_COLOR
        e.control.update()

    
    def _on_enter_blur(self, e: ControlEvent) -> None:
        """
        При потери фокуса открывает основное содержимое
        """
        old_value = self.value
        value = self.ref_enter_textfield.current.value
        if self.is_valid_value(value):
            self.value = self.min_max_check(float(value))
            self.ref_main_control_value.current.value = self.value
        else:
            self.ref_enter_textfield.current.value = self.value

        self.main_control.visible = True
        self.enter_control.visible = False

        self.ref_main_control_value.current.color = None
        self.main_control.bgcolor = self.MAIN_COLOR
        self.update()
        if old_value != self.value:
            self._on_change()

    
    def _on_enter_change(self, e: ControlEvent) -> None:
        """
        При изменении значения в поле ввода
        """
        # TODO: можно добавить проверку на валидность
        pass

    
    def set_connect_state(self, is_connected: bool, is_recalculate: bool = True) -> None:
        """
        Переключает состояние подключения
        """
        self.is_connected = is_connected
        self.main_control.visible = not self.is_connected
        self.enter_control.visible = not self.is_connected
        self.connected_control.visible = self.is_connected
        self.update()
        if is_recalculate:
            self._on_change()


    def is_valid_value(self, value: str) -> bool:
        """
        Проверяет значение на валидность
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
        

    def min_max_check(self, value: float) -> float:
        """
        Проверяет значение на валидность
        """
        if self.min_value is not None and value < self.min_value:
            value = self.min_value
        if self.max_value is not None and value > self.max_value:
            value = self.max_value
        if self.decimal_accuracy is None:
            return float(value)
        elif self.decimal_accuracy == 0:
            return int(value)
        return round(float(value), self.decimal_accuracy)
        

    def drag_value_update(self, e: DragUpdateEvent) -> None:
        """
        При изменении значения в поле ввода
        """
        value_text: Text = self.ref_main_control_value.current
        step = self.value_step
        cur_value = float(value_text.value)
        round_num = max(
            len(str(step).lstrip('0').replace('.', '')),
            len(str(cur_value).lstrip('0').replace('.', ''))
        )
        if keyboard.is_pressed('shift'):
            round_num += 3
            step = round(self.value_step / 1000, round_num)

        value = round(cur_value + round(e.delta_x) * step, round_num)
        value_text.value =  self.min_max_check(value)
        value_text.update()


    def drag_value_update_start(self, e: DragUpdateEvent) -> None:
        """
        При начале изменения значения в поле ввода
        """
        self.is_drag_changed = True
        value_text: Text = self.ref_main_control_value.current
        value_text.color = self.ACCENT_COLOR
        value_text.update()
        

    def drag_value_update_end(self, e: DragUpdateEvent) -> None:
        """
        При окончании изменения значения в поле ввода
        """
        self.is_drag_changed = False
        value_text: Text = self.ref_main_control_value.current
        value_text.color = None
        value_text.update()

        if self.value != float(value_text.value):
            self.value = self.min_max_check(value_text.value)
            self._on_change()
