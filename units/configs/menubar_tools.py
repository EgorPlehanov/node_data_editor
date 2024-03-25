from .folder import Folder

from dataclasses import dataclass
from typing import Callable
from flet import icons, colors



@dataclass
class Tool:
    """
    Инструмент со вкладки инструментов в меню

    name - название инструмента
    icon - иконка инструмента
    color - цвет инструмента (в меню)
    function - функция инструмента
    """

    name: str = "Untitled"
    icon: str = icons.QUESTION_MARK
    color: str = colors.WHITE
    function: Callable = lambda: None



class MenubarTools:
    """
    Список инструментов в меню
    """

    @staticmethod
    def get_menubar_tools():
        return MenubarTools.menubar_tools

    
    menubar_tools = [
        Folder(
            name = "Масштабирование",
            icon = icons.SEARCH,
            obj_list = [
                Tool(
                    name = "Увеличить",
                    icon = icons.ZOOM_IN,
                    function = lambda self: print("Увеличить")
                ),

                Tool(
                    name = "Уменьшить",
                    icon = icons.ZOOM_OUT,
                    function = lambda self: print("Уменьшить")
                ),
                
                Tool(
                    name = "Сбросить масштаб",
                    icon = icons.SETTINGS_OVERSCAN,
                    function = lambda self: print("Сбросить масштаб")
                ),

            ]
        ),

        Folder(
            name = "Выделение",
            icon = icons.CONTROL_POINT_DUPLICATE,
            obj_list = [
                Tool(
                    name = "Выбрать все",
                    icon = icons.SELECT_ALL,
                    function = lambda self: self.workplace.node_area.select_all()
                ),

                Tool(
                    name = "Снять выделение",
                    icon = icons.DESELECT,
                    function = lambda self: self.workplace.node_area.clear_selection()
                ),

                Tool(
                    name = "Инвертировать выделение",
                    icon = icons.SWAP_HORIZ,
                    function = lambda self: self.workplace.node_area.invert_selection()
                ),

                Tool(
                    name = "Переместить выделеные в начало",
                    icon = icons.CENTER_FOCUS_STRONG_SHARP,
                    function = lambda self: self.workplace.node_area.move_selection_to_start()
                ),

                Tool(
                    name = "Удалить выделенные",
                    icon = icons.DELETE_SWEEP,
                    function = lambda self: self.workplace.node_area.delete_selected_nodes()
                )
            ]
        )
    ]
