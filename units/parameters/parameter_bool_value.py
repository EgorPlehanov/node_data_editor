from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from .parameter_typing import *
from ..data_types import ParameterConnectType

from flet import *
from dataclasses import dataclass



@dataclass
class BoolValueParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра с одним булевым значением

    default_value - значение параметра (по умолчанию)
    is_tristate - третий статус (True, False, None)
    """
    
    default_value: bool = False
    is_tristate: bool = False

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.BOOL_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN



class BoolValueParam(Container, ParameterInterface):
    '''
    Параметр с одним булевым значением
    '''

    def __init__(
        self,
        node: 'Node',
        config: BoolValueParamConfig = BoolValueParamConfig()
    ):
        self._type: ParameterType = ParameterType.BOOL_VALUE
        self._connect_type: ParameterConnectType = ParameterConnectType.IN

        self.node = node
        self._config: BoolValueParamConfig = config

        super().__init__()
        self.__post_init__()
        
        self.set_style()
        
        self.main_control = self._create_main_control()
        self.connected_control = self._create_connected_control()

        self.content = self._create_content()

        if self._config.has_connect_point:
            self.connect_point = self._create_connect_point()



    def set_style(self) -> None:
        """
        Устанавливает стиль параметра
        """
        self.is_tristate = self._config.is_tristate
        
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
                self.connected_control,
            ],
            spacing = 0
        )
        

    def _create_main_control(self) -> Container:
        '''
        Создает основное содержимое параметра
        '''
        self.ref_main_control_value = Ref[Checkbox]()
        return Container(
            on_click = self._change_checkbox_value,
            on_hover = self._on_main_control_hover,
            visible = not self.is_connected,
            content = Row(
                vertical_alignment = CrossAxisAlignment.CENTER,
                alignment = MainAxisAlignment.SPACE_BETWEEN,
                controls = [
                    Text(self.name),
                    Checkbox(
                        ref = self.ref_main_control_value,
                        value = self.value,
                        height = self.control_height,
                        tristate = self.is_tristate,
                        check_color = colors.WHITE,
                        active_color = colors.with_opacity(0, colors.WHITE),
                        overlay_color = colors.WHITE10,
                        disabled=True
                    )
                ],
            ),
            padding = padding.only(left = 5),
            bgcolor = self.MAIN_COLOR
        )
    
    
    def _create_connected_control(self) -> Container:
        '''
        Создает содержимое параметра когда он подключен
        '''
        return Container(
            visible = self.is_connected,
            content = Row([
                Text(self.name)
            ]),
            padding = padding.only(left = 5, right = 5),
        )
    

    def _on_main_control_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на основное содержимое
        '''
        self.ref_main_control_value.current.check_color = self.ACCENT_COLOR if e.data == "true" else colors.WHITE
        e.control.bgcolor = self.HOVER_COLOR if e.data == "true" else self.MAIN_COLOR
        e.control.update()

    
    def set_connect_state(self, is_connected: bool, is_recalculate: bool = True) -> None:
        """
        Переключает состояние подключения
        """
        self.is_connected = is_connected
        self.main_control.visible = not self.is_connected
        self.connected_control.visible = self.is_connected
        self.update()
        if is_recalculate:
            self._on_change()


    def on_checkbox_change(self, e: ControlEvent) -> None:
        """
        Обработчик изменения состояния
        """
        self.value = e.control.value
        self._on_change()

    
    def _change_checkbox_value(self, e: ControlEvent) -> None:
        '''
        Изменяет состояние параметра при клике на поле параметра
        '''
        self.value = (
            not self.value if not self.is_tristate
            else {False: True, True: None, None: False}[self.value]
        )
        self.ref_main_control_value.current.value = self.value
        self.update()
        self._on_change()

