from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from flet import *
from dataclasses import dataclass, field
from typing import List

from .parameter_typing import *
from ..node.node_connect_point import ParameterConnectType

@dataclass
class DropdownOptionItem:
    key: str    = ''
    text: str   = 'Не задано'

@dataclass
class DropdownValueParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра с одним выподающим списком

    default_value - значение параметра (по умолчанию)
    """
    height: int = 30
    default_value: str = None
    include_none: bool = False
    options: List[DropdownOptionItem] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.DROPDOWN_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN



class DropdownValueParam(Container, ParamInterface):
    '''
    Параметр с одним булевым значением
    '''
    def __init__(self, node: 'Node', config: DropdownValueParamConfig = DropdownValueParamConfig()):
        self._type: ParameterType = ParameterType.BOOL_VALUE
        self._connect_type: ParameterConnectType = ParameterConnectType.IN

        self.node = node
        self._config: DropdownValueParamConfig = config
        super().__init__()
        
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
        self.__post_init__()

        self.options = self._config.options
        self.include_none = self._config.include_none
        if self.include_none:
            self.options.insert(0, DropdownOptionItem(key = None, text = 'Не задано'))
        elif self.value is None:
            self.value = self.options[0].key

        self.key_to_text = {option.key: option.text for option in self.options}

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
        self.ref_main_control_value = Ref[Dropdown]()
        self.ref_main_control_value_icon = Ref[Icon]()
        self.ref_main_control_value_container = Ref[Container]()
        self.ref_main_control_value_popup = Ref[PopupMenuButton]()
        return Container(
            expand = True,
            on_hover = self._on_main_control_hover,
            visible = not self.is_connected,
            content = Row(
                vertical_alignment = CrossAxisAlignment.CENTER,
                controls = [
                    Text(self.name),
                    PopupMenuButton(
                        ref = self.ref_main_control_value_popup,
                        tooltip = self.key_to_text[self.value],
                        expand = True,
                        content = Container(
                            ref = self.ref_main_control_value_container,
                            on_hover = self._on_main_control_dropdown_hover,
                            height = self.control_height,
                            border_radius = 5,
                            padding = padding.only(right = 5),
                            border = border.all(1, colors.with_opacity(0, colors.BLACK)),
                            content = Row(
                                vertical_alignment = CrossAxisAlignment.CENTER,
                                spacing = 0,
                                controls = [
                                    Icon(
                                        ref = self.ref_main_control_value_icon,
                                        name = icons.ARROW_DROP_DOWN,
                                        color = colors.WHITE,
                                    ),
                                    Text(
                                        expand = True,
                                        ref = self.ref_main_control_value,
                                        value = self.key_to_text[self.value],
                                        text_align = TextAlign.RIGHT,
                                        no_wrap = True,
                                        max_lines = 1,
                                    )
                                ]
                            )
                        ),
                        items = [
                            PopupMenuItem(
                                text = option.text,
                                on_click = self.on_dropdown_change,
                                data = option.key
                            )
                            for option in self.options
                        ]
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
            content = Row([Text(self.name)]),
            padding = padding.only(left = 5, right = 5),
        )
    

    def _on_main_control_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на основное содержимое
        '''
        is_hover = e.data == "true"
        self.ref_main_control_value.current.color = self.ACCENT_COLOR if is_hover else None
        e.control.bgcolor = self.HOVER_COLOR if is_hover else self.MAIN_COLOR
        self.update()


    def _on_main_control_dropdown_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на кнопку выбора основное содержимое
        '''
        is_hover = e.data == "true"
        self.ref_main_control_value_icon.current.color = self.ACCENT_COLOR if is_hover else colors.WHITE
        self.ref_main_control_value_container.current.border = (
            border.all(1, self.ACCENT_COLOR) if is_hover
            else border.all(1, colors.with_opacity(0, colors.BLACK))
        )
        self.update()

    
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


    def on_dropdown_change(self, e: ControlEvent) -> None:
        """
        Обработчик изменения состояния
        """
        if e.control.data != self.value:
            self.value = e.control.data

            value_text = self.key_to_text[self.value]
            self.ref_main_control_value.current.value = value_text
            self.ref_main_control_value_popup.current.tooltip = value_text
            self.update()

            self._on_change()
