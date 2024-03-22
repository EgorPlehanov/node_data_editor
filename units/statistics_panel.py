from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .workplace import Workplace

from flet import *
from typing import Callable, Any, Dict, List



class NodeStatistParam(Container):
    def __init__(self,
        key: str,
        value: Any = '',
        name: str = None,
        values_not_shown: List = [],
        show_when: Callable = None,
        to_string: Callable = None,
        prefix: str = None,
        postfix: str = None,
        text_color: str = colors.WHITE54,
        bgcolor: str = None,
        border_color: str = None,
        tooltip: str = None,
    ):
        super().__init__()
        self.key = key
        self.value = value
        self.name = name if name is not None else key

        self.values_not_shown = values_not_shown
        self.values_not_shown.extend([str(value) for value in values_not_shown])
        self.show_when = show_when if show_when is not None else self.default_show_when
        self.to_string = to_string

        self.prefix = prefix if prefix is not None else ''
        self.postfix = postfix if postfix is not None else ''

        self.text_color = text_color
        self.bgcolor = bgcolor
        self.tooltip = tooltip
        self.border_color = border_color
        self.visible = self.show_when()
        self.content = self.create_content()
        self.set_style()


    def set_style(self):
        self.alignment = alignment.center
        self.padding = padding.only(left = 5, right = 5)
        self.border_radius = 5
        if self.border_color is not None:
            self.border = border.all(1, self.border_color)


    def default_show_when(self) -> bool:
        return self.value not in self.values_not_shown and str(self.value) not in self.values_not_shown


    def __str__(self) -> str:
        if self.to_string is None:
            return f"{self.name}:\u00A0{self.prefix}{self.value}{self.postfix}"
        return self.to_string(self.value)


    def create_content(self) -> Control:
        self.ref_statistics_text = Ref[Text]()
        return Text(
            ref = self.ref_statistics_text,
            value = str(self),
            selectable = True,
            expand = True,
            color = self.text_color,
            theme_style = TextThemeStyle.BODY_MEDIUM
        )
    

    def update_text(self, value: Any):
        self.value = value
        if self.show_when():
            self.visible = True
            self.ref_statistics_text.current.value = str(self)
        else:
            self.visible = False



class NodeStatisticsPanel(Row):

    def __init__(self, page: Page, workplace: "Workplace"):
        super().__init__()
        self.data: Dict[str, NodeStatistParam] = self.create_statistics_data()
        self.controls = self.create_controls()
    

    def create_statistics_data(self):
        '''
        Создает словарь с данными для панели статистики
        '''
        def cycles_to_string(value):
            unique_cycles = [list(item) for item in list(set(map(tuple, value)))]
            cycles_str = []
            for cycle in unique_cycles:
                cycle.append(cycle[0])
                cycles_str.append('(' + '->'.join([f'{e.id}' for e in cycle]) + ')')
            return f"Циклов ({len(unique_cycles)}): {'; '.join(cycles_str)}"
        
        return {
            param.key: param
            for param in [
                NodeStatistParam("nodes", 0, "Узлов", values_not_shown=[0]),
                NodeStatistParam("edges", 0, "Соединений", values_not_shown=[0]),
                NodeStatistParam("scale", 1, "Масштаб", values_not_shown=[1], prefix='x'),
                NodeStatistParam("selected", 0, "Выбрано", values_not_shown=[0]),
                NodeStatistParam(
                    "cycles", [], "Циклов", values_not_shown=[[]],
                    tooltip = "Функции не могут быть пересчитаны пока есть циклы",
                    to_string = cycles_to_string, text_color=colors.RED,
                    bgcolor = colors.with_opacity(0.1, colors.RED_300),
                ),
            ]
        }


    def create_controls(self) -> List[Control]:
        return [stat_param for stat_param in self.data.values()]


    def add_stat_param(self, param: NodeStatistParam):
        '''
        Добавляет параметр в панель статистики
        '''
        if param.key not in self.data.keys():
            self.data[param.key] = param
    

    def update_text(self, attribute: str, value: str) -> None:
        '''
        Обновляет содержимое панели статистики
        '''
        if attribute in self.data.keys():
            if self.data[attribute].value == value:
                return
            self.data[attribute].update_text(value)

        self.update()