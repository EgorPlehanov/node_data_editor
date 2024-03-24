from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from .parameter_typing import *
from ..data_types import ParameterConnectType

from flet import *
from dataclasses import dataclass



@dataclass
class TextValueParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра с одним текстовым значением

    default_value - значение параметра (по умолчанию)
    text_align - выравнивание текста
    capitalization - капитализация текста
    hint_text - подсказка
    """
    
    default_value: str = ''
    capitalization: TextCapitalization = TextCapitalization.NONE
    hint_text: str = ''

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.TEXT_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN



class TextValueParam(Container, ParameterInterface):
    '''
    Параметр с одним булевым значением
    '''

    def __init__(
        self,
        node: 'Node',
        config: TextValueParamConfig = TextValueParamConfig()
    ):
        self._type: ParameterType = ParameterType.TEXT_VALUE
        self._connect_type: ParameterConnectType = ParameterConnectType.IN

        self.node = node
        self._config: TextValueParamConfig = config
        
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
        self.capitalization = self._config.capitalization
        self.hint_text = self._config.hint_text

        self.is_enter_focused = False

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
        self.ref_main_control_value = Ref[TextField]()
        return Container(
            on_hover = self._on_main_control_hover,
            visible = not self.is_connected,
            content = Row(
                controls = [
                    Text(self.name),
                    TextField(
                        ref = self.ref_main_control_value,
                        expand = True,
                        value = str(self.value),
                        focused_border_width = 1,
                        focused_border_color = self.ACCENT_COLOR,
                        content_padding = padding.only(left = 5, right = 5),
                        border_color = colors.with_opacity(0, colors.BLACK),
                        height = self.control_height,
                        text_size = self.control_height * 0.75,
                        text_align = TextAlign.RIGHT,
                        capitalization = self.capitalization,
                        hint_text = self.hint_text,
                        on_blur = self._on_enter_blur,
                        on_focus = self._on_enter_focus,
                    )
                ]
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
    

    def _on_enter_focus(self, e: ControlEvent) -> None:
        '''
        При фокусе изменяет цвет
        '''
        self.is_enter_focused = True
        self.set_main_control_bgcolor()

    
    def set_main_control_bgcolor(self, is_hover: bool = False) -> None:
        '''
        Устанавливает цвет основного контрола
        '''
        self.main_control.bgcolor = (
            None if self.is_enter_focused
            else (self.HOVER_COLOR if is_hover else self.MAIN_COLOR)
        )
        self.ref_main_control_value.current.text_align = (
            TextAlign.LEFT if self.is_enter_focused else TextAlign.RIGHT
        )
        self.ref_main_control_value.current.color = self.ACCENT_COLOR if is_hover and not self.is_enter_focused else None
        self.main_control.update()


    def _on_main_control_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на основное содержимое
        '''
        self.set_main_control_bgcolor(is_hover = e.data == "true")

    
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


    def _on_enter_blur(self, e: ControlEvent) -> None:
        """
        При потери фокуса открывает основное содержимое
        """
        value = self.ref_main_control_value.current.value
        if value != self.value:
            self.value = value
            self._on_change()

        self.is_enter_focused = False
        self.set_main_control_bgcolor()
    