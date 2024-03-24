from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from .configs import *
from ..node import NodeConfig

from flet import *
from typing import List



class FunctionMenuBar(MenuBar):
    """
    Меню бар приложения
    Содержит пункты меню: ноды, инструменты
    """

    def __init__(
        self,
        page: Page,
        workplace: "Workplace"
    ):
        super().__init__()
        self.page = page
        self.workplace = workplace

        self.expand = True
        self.controls = self.create_controls()

        self.menu_style = MenuStyle(
            shadow_color = colors.BLACK38,
            bgcolor={
                MaterialState.HOVERED: colors.WHITE,
                MaterialState.FOCUSED: colors.BLUE,
                MaterialState.DEFAULT: colors.BLACK87,
            }
        )


    def create_controls(self) -> List[SubmenuButton | MenuItemButton]:
        """
        Создание списка пунктов меню
        """
        return [
            SubmenuButton(
                content = Row([Icon(icons.ADD_CARD), Text("Ноды")]),
                controls = self.create_submenu(
                    NodeLibrary.get_nodes_configs()
                )
            ),
            SubmenuButton(
                content = Row([Icon(icons.HARDWARE), Text("Инструменты")]),
                controls = self.create_submenu(
                    MenubarTools.get_menubar_tools()
                )
            )
        ]
    

    def create_submenu(self, obj_list: List[Folder | Tool | NodeConfig]) -> List[SubmenuButton | MenuItemButton]:
        """
        Создание подменю
        """
        items = []
        for obj in obj_list:
            if isinstance(obj, Folder):
                items.append(
                    SubmenuButton(
                        content = Row([Icon(obj.icon, color=obj.color), Text(obj.name)]),
                        controls = self.create_submenu(obj.obj_list)
                    )
                )
            else:
                items.append(self.create_menu_item_button(obj))
        return items
    


    def create_menu_item_button(self, obj: Tool | NodeConfig) -> MenuItemButton:
        """
        Создание пункта меню
        """
        row_controls = []
        if obj.icon:
            row_controls.append(Icon(obj.icon, color=obj.color))

        row_controls.append(Text(obj.name))

        is_has_counter = not isinstance(obj, Tool)
        ref_text_counter = Ref[Text]()
        if is_has_counter:
            row_controls.append(
                Text(ref=ref_text_counter, data=1, visible=False, color=colors.BLACK)
            )
        button_content = GestureDetector(
            content = Row(row_controls),
            on_scroll = lambda e: self.on_item_button_scroll(e, ref_text_counter) if is_has_counter else None,
            on_exit = lambda e: self.on_item_button_exit(e, ref_text_counter) if is_has_counter else None
        )
        return MenuItemButton(
            content = button_content,
            style = ButtonStyle(bgcolor={MaterialState.HOVERED: colors.BLUE}),
            on_click = lambda e: self.on_item_button_click(obj, ref_text_counter)
        )
    

    def on_item_button_scroll(self, e: ScrollEvent, ref_text_counter: Ref[Text]) -> None:
        """
        При скролле с наведенным курсором на пункт меню
        """
        counter_text = ref_text_counter.current
        counter_text.data += -1 if e.scroll_delta_y > 0 else 1
        counter_text.data = max(1, counter_text.data)
        counter_text.data = min(10, counter_text.data)
        counter_text.value = f"x{counter_text.data}"
        counter_text.visible = counter_text.data != 1
        counter_text.update()


    def on_item_button_exit(self, e: ControlEvent, ref_text_counter: Ref[Text]) -> None:
        """
        При уходе курсора с пункта меню
        """
        ref_text_counter.current.data = 1
        ref_text_counter.current.visible = False
        ref_text_counter.current.update()


    def on_item_button_click(self, obj, ref_text_counter: Ref[Text]) -> None:
        """
        При нажатии на пункт меню
        """
        if isinstance(obj, Tool):
            obj.function(self)
        else:
            self.workplace.node_area.add_node(config=obj, ref_text_counter=ref_text_counter)
            self.on_item_button_exit(None, ref_text_counter)
    