from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.node import Node

from .parameter_typing import *
from ..data_types import File, ParameterConnectType

from flet import *
from dataclasses import dataclass, field
from typing import List



@dataclass
class FilePickerParamConfig(ParameterConfigInterface):
    """
    Конфигурация параметра выбра файла

    default_value - значение параметра (по умолчанию)
    initial_directory - директория, в которой открывается окно выбора файла
    file_type - тип выбираемого файла
    allowed_extensions - допустимые расширения выбираемого файла
    """

    height: int = 30
    default_value: File = None
    dialog_title: str = 'Выбор файла'
    initial_directory: str          = None
    file_type: FilePickerFileType   = FilePickerFileType.CUSTOM
    allowed_extensions: List[str]   = field(default_factory=lambda: [
        'png', 'jpg', "jpeg", "png", "bmp", "gif", "xcr", "bin"
    ])

    def __post_init__(self):
        super().__post_init__()

    @property
    def type(self) -> ParameterType:
        return ParameterType.FILE_PICKER_VALUE
    
    @property
    def connect_type(self) -> ParameterType:
        return ParameterConnectType.IN



class FilePickerParam(Container, ParameterInterface):
    '''
    Параметр с одним булевым значением
    '''
    
    def __init__(
        self,
        node: 'Node',
        config: FilePickerParamConfig = FilePickerParamConfig()
    ):
        self._type: ParameterType = ParameterType.FILE_PICKER_VALUE
        self._connect_type: ParameterConnectType = ParameterConnectType.IN

        self.node = node
        self._config: FilePickerParamConfig = config

        super().__init__()
        self.__post_init__()

        self.set_style()
        
        self.main_control = self._create_main_control()
        self.connected_control = self._create_connected_control()
        self.file_picker_dialog = self._create_file_picker_dialog()

        self.content = self._create_content()

        if self._config.has_connect_point:
            self.connect_point = self._create_connect_point()

        if self._config.default_value is not None:
            self.list_picked_files



    def set_style(self) -> None:
        """
        Устанавливает стиль параметра
        """
        self.dialog_title = self._config.dialog_title
        self.initial_directory = self._config.initial_directory
        self.file_type = self._config.file_type
        self.allowed_extensions = self._config.allowed_extensions

        self.list_picked_files: List[File] = [] if self.value is None else [self.value]

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
        return Container(
            on_hover = self._on_main_control_hover,
            visible = not self.is_connected,
            padding = padding.only(left = 5),
            bgcolor = self.MAIN_COLOR,
            content = Row(
                height = self.control_height,
                vertical_alignment = CrossAxisAlignment.CENTER,
                spacing = 5,
                controls = [
                    Text(self.name),
                    self.create_main_control_history_button(),
                    self.create_main_control_open_button(),
                    self.create_main_control_file_view(),
                ],
            ),
        )
    

    def create_main_control_history_button(self) -> Container:
        '''
        Создает кнопку истории
        '''
        self.ref_main_control_history_button = Ref[IconButton]()
        self.ref_main_control_history_popup = Ref[PopupMenuButton]() 
        history_button = Icon(
            ref = self.ref_main_control_history_button,
            name = icons.HISTORY,
            size = 20,
            color = colors.GREY_700 if len(self.list_picked_files) == 0 else colors.WHITE
        )
        hover_history_button = Container(
            on_hover = lambda e: self.on_history_button_hover(
                ref_history_button = self.ref_main_control_history_button,
                is_hover = e.data == "true"
            ),
            content = history_button,
        )
        return PopupMenuButton(
            ref = self.ref_main_control_history_popup,
            content = hover_history_button,
            items = self.get_history_popup_menu_items(),
            tooltip = 'История выбора файла',
            on_cancelled = self.update_history
        )
    

    def on_history_button_hover(self, ref_history_button: Ref[IconButton], is_hover: bool):
        '''
        Обработчик наведения на кнопку истории
        '''
        ref_history_button.current.color = (
            colors.GREY_700 if len(self.list_picked_files) == 0
            else (self.ACCENT_COLOR if is_hover else colors.WHITE)
        )
        ref_history_button.current.update()
    

    def get_history_popup_menu_items(self) -> List[PopupMenuItem]:
        '''
        Возвращает список пунктов меню истории
        '''
        return [
            self.create_history_popup_menu_item(file, idx)
            for idx, file in enumerate(self.list_picked_files)
        ]
    

    def create_history_popup_menu_item(self, file: File, idx: int) -> PopupMenuItem:
        '''
        Создает пункт меню истории
        '''
        delete_message = Row(
            visible = False,
            controls = [Text(value="Удалено", expand=True, text_align=TextAlign.CENTER)],
        )
        file_image = Image(src=file.path, height=100, width=100, border_radius=3, fit=ImageFit.CONTAIN)
        file_name = Text(value=file, expand=True, size=14, selectable=True)
        file_path = Text(value=file.path, size=10, selectable=True)
        ref_close_button = Ref[IconButton]()
        close_button = IconButton(
            ref = ref_close_button,
            icon = icons.CLOSE,
            icon_color = colors.WHITE,
            icon_size = 20,
            width = 20,
            height = 20,
            style = ButtonStyle(padding = 0),
            on_click = (
                lambda file, idx: lambda _: self.remove_file_from_history(file, idx)
            )(file, idx),
        )
        hover_close_button = self.create_hover_conteiner(
            control = close_button,
            ref_control = ref_close_button,
        )
        return PopupMenuItem(
            data = idx,
            content = Column([
                delete_message,
                Row([
                    file_image,
                    Column(
                        expand = True,
                        controls = [
                            Row(
                                vertical_alignment = CrossAxisAlignment.START,
                                controls = [file_name, hover_close_button]
                            ),
                            file_path
                        ],
                    ),
                ]),
            ]),
            on_click = (lambda file: lambda _: self.file_update(file))(file),
        )


    def create_main_control_open_button(self) -> Container:
        '''
        Создает кнопку открытия
        '''
        self.ref_main_control_open_button = Ref[IconButton]()
        self.ref_main_control_open_button_text = Ref[Text]()
        self.ref_main_control_open_button_container = Ref[Container]()
        open_button = IconButton(
            ref = self.ref_main_control_open_button,
            icon = icons.FOLDER,
            icon_color = colors.WHITE,
            icon_size = 20,
            width = 20,
            height = 20,
            disabled = True,
            style = ButtonStyle(
                padding = 0,
                overlay_color = colors.with_opacity(0, colors.WHITE)
            ),
        )
        open_button_text = Text(
            ref = self.ref_main_control_open_button_text,
            value = "Открыть файл",
            expand = True,
            text_align = TextAlign.CENTER,
            visible = self.value is None
        )
        hover_open_button = self.create_hover_conteiner(
            control = Row([open_button, open_button_text]),
            ref_control = self.ref_main_control_open_button,
            ref_text = self.ref_main_control_open_button_text,
            ref_container = self.ref_main_control_open_button_container,
            is_hover_conteiner = True
        )
        hover_open_button.on_click = self.open_file_picker
        hover_open_button.expand = self.value is None
        hover_open_button.border_radius = 5
        hover_open_button.margin = margin.only(right = 5) if self.value is None else None
        return hover_open_button
    

    def create_main_control_file_view(self) -> Container:
        '''
        Создает представление выбранного файла
        '''
        self.ref_main_control_file_container = Ref[Container]()
        self.ref_main_control_close_button = Ref[IconButton]()
        self.ref_main_control_file_name = Ref[Text]()
        self.ref_main_control_file_preview = Ref[Image]()
        self.ref_main_control_file_image = Ref[Image]()
        self.ref_main_control_file_popup_button = Ref[PopupMenuButton]()
        close_button = IconButton(
            ref = self.ref_main_control_close_button,
            icon = icons.CLOSE,
            icon_color = colors.WHITE,
            icon_size = 20,
            width = 20,
            height = 20,
            style = ButtonStyle(
                padding = 0,
                overlay_color = colors.with_opacity(0, colors.WHITE)
            ),
            on_click = self.close_select_file,
        )
        hover_close_button = self.create_hover_conteiner(
            control = close_button,
            ref_control = self.ref_main_control_close_button,
        )
        file_name = Row(
            expand = True,
            scroll = ScrollMode.HIDDEN,
            controls = [Text(
                ref = self.ref_main_control_file_name,
                value = self.value.formatted_name if self.value is not None else "",
                selectable = True,
                text_align = TextAlign.RIGHT
            )]
        )
        file_preview = Container(
            padding = padding.only(top=3, bottom=3),
            content = PopupMenuButton(
                ref = self.ref_main_control_file_popup_button,
                tooltip = self.value.formatted_name if self.value is not None else None,
                content = Image(
                    ref = self.ref_main_control_file_preview,
                    src = self.value.path if self.value is not None else None,
                    fit = ImageFit.FIT_HEIGHT,
                    border_radius = 3,
                ),
                items = [
                    PopupMenuItem(
                        content = Image(
                            ref = self.ref_main_control_file_image,
                            src = self.value.path if self.value is not None else None,
                            fit = ImageFit.CONTAIN,
                            width = 260,
                            border_radius = 5,
                        )
                    )
                ],
            )
        )
        return Container(
            ref = self.ref_main_control_file_container,
            visible = self.value is not None,
            expand = True,
            padding = padding.only(right = 5),
            border_radius = border_radius.all(5),
            content = Row(
                vertical_alignment = CrossAxisAlignment.CENTER,
                spacing = 5,
                controls = [
                    hover_close_button,
                    file_name,
                    file_preview
                ],
            ),
        )
    

    def create_hover_conteiner(
        self,
        control: Control,
        ref_control: Ref,
        ref_text: Ref = None,
        ref_container: Ref = None,
        is_hover_conteiner: bool = False
    ) -> Container:
        '''
        Создает hover контейнер
        '''
        return Container(
            ref = ref_container,
            on_hover = lambda e: self.on_button_hover(
                is_hover = e.data == "true",
                icon_button = ref_control.current if ref_control else None,
                text = ref_text.current if ref_text else None,
                container = e.control if is_hover_conteiner else None
            ),
            content = control,
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
    

    def on_button_hover(
        self, is_hover: bool,
        icon_button: IconButton, text: Text = None, container: Container = None
    ) -> None:
        """
        Обработчик наведения на кнопку
        """
        if icon_button:
            if isinstance(icon_button, Icon):
                icon_button.color = self.ACCENT_COLOR if is_hover else colors.WHITE
            else:
                icon_button.icon_color = self.ACCENT_COLOR if is_hover else colors.WHITE
        if text:
            text.color = self.ACCENT_COLOR if is_hover else colors.WHITE
        if container:
            container.border = (
                border.all(1, self.ACCENT_COLOR) if is_hover and not self.value
                else border.all(1, colors.with_opacity(0, colors.BLACK))
            )
        self.update()
    

    def _on_main_control_hover(self, e: ControlEvent) -> None:
        '''
        При наведении на основное содержимое
        '''
        e.control.bgcolor = self.HOVER_COLOR if e.data == "true" else self.MAIN_COLOR
        self.ref_main_control_file_name.current.color = self.ACCENT_COLOR if e.data == "true" else colors.WHITE
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


    def _create_file_picker_dialog(self) -> FilePicker:
        '''Создает диалоговое окно выбора файлов'''
        file_picker_dialog = FilePicker(
            on_result = self.on_file_selected,
        )
        self.node.page.overlay.append(file_picker_dialog)
        self.node.page.update()
        return file_picker_dialog


    def open_file_picker(self, e: ControlEvent) -> None:
        '''Открывает диалоговое окно выбора файлов'''
        self.file_picker_dialog.pick_files(
            dialog_title        = self.dialog_title,
            initial_directory   = self.initial_directory,
            file_type           = self.file_type,
            allowed_extensions  = self.allowed_extensions,
            allow_multiple      = False,
        )


    def on_file_selected(self, e: FilePickerResultEvent) -> None:
        '''
        Обработчик выбора файла
        '''
        if e.files is not None:
            file = File(e.files[0].path)
            self.file_update(file)


    def file_update(self, file: File) -> None:
        '''
        Обновляет список выбранных файлов, представление и состояние файла
        '''
        if file == self.value:
            return
        self.value = file
        self.move_file_to_top(file)
        self.update_file_view()
        self.toggle_file_view(is_file_opened = True)
        self.on_history_button_hover(self.ref_main_control_history_button, False)
        self._on_change()


    def move_file_to_top(self, file: File) -> None:
        """
        Перемещает или добавляет (для новых) файл в начало списка
        """
        if file in self.list_picked_files:
            self.list_picked_files.remove(file)
        self.list_picked_files.insert(0, file)


    def toggle_file_view(self, is_file_opened: bool) -> None:
        '''
        Переключает видимость окна файла
        '''
        self.ref_main_control_open_button_container.current.expand = not is_file_opened
        self.ref_main_control_open_button_text.current.visible = not is_file_opened
        self.ref_main_control_file_container.current.visible = is_file_opened
        self.ref_main_control_close_button.current.icon_color = colors.WHITE
        self.ref_main_control_open_button_container.current.margin = (
            margin.only(right = 5) if self.value is None else None
        )
        self.update()


    def update_file_view(self) -> None:
        '''
        Обновляет содержимое окна файла
        '''
        self.ref_main_control_file_name.current.value = self.value
        self.ref_main_control_file_preview.current.src = self.value.path
        self.ref_main_control_file_image.current.src = self.value.path
        self.ref_main_control_file_popup_button.current.tooltip = self.value.formatted_name

        self.ref_main_control_history_popup.current.items = self.get_history_popup_menu_items()
        self.update()


    def close_select_file(self, e: ControlEvent) -> None:
        '''
        Закрывает представление файла
        '''
        self.value = None
        self.toggle_file_view(is_file_opened = False)
        self._on_change()
        

    def remove_file_from_history(self, file: File, idx) -> None:
        '''
        Удаляет файл из истории
        '''
        self.list_picked_files.remove(file)

        popup_items = self.ref_main_control_history_popup.current.items
        removed_item = popup_items[idx]
        removed_item.on_click = self.update_history
        removed_item.content.controls[0].visible = True
        removed_item.content.controls[1].visible = False
        removed_item.update()


    def update_history(self, e: ControlEvent) -> None:
        '''
        Обновляет историю выбора
        '''
        self.ref_main_control_history_popup.current.items = self.get_history_popup_menu_items()
        self.on_history_button_hover(self.ref_main_control_history_button, False)
        self.update()