from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .workplace import Workplace

from flet import *
from typing import Callable, Any, Dict, List



class NodeStatistParam:
    def __init__(self,
        key: str,
        value: Any = '',
        name: str = None,
        values_not_shown: List = [],
        show_when: Callable = None,
        prefix: str = None,
        postfix: str = None,
    ):
        self.key = key
        self.value = value
        self.name = name if name is not None else key

        self.values_not_shown = values_not_shown
        self.values_not_shown.extend([str(value) for value in values_not_shown])
        self.show_when = show_when if show_when is not None else self.default_show_when

        self.prefix = prefix if prefix is not None else ''
        self.postfix = postfix if postfix is not None else ''

    def default_show_when(self) -> bool:
        return self.value not in self.values_not_shown and str(self.value) not in self.values_not_shown

    def __str__(self) -> str:
        return f"{self.name}:\u00A0{self.prefix}{self.value}{self.postfix}"



class NodeStatisticsPanel(Row):

    def __init__(self, page: Page, workplace: "Workplace"):
        super().__init__()
        self.data: Dict[str, NodeStatistParam] = self.create_statistics_data()
        self.controls = self.create_controls()


    def create_controls(self) -> List[Control]:
        self.ref_statistics_text = Ref[Text]()
        return [
            Text(
                ref = self.ref_statistics_text,
                value = self.get_text(),
                selectable = True,
                expand = True,
                # max_lines = 5,
                # overflow = TextOverflow.VISIBLE,
                color = colors.WHITE54,
                theme_style = TextThemeStyle.BODY_MEDIUM
            ),
        ]
    

    def create_statistics_data(self):
        '''Создает словарь с данными для панели статистики'''
        return {
            param.key: param
            for param in [
                NodeStatistParam("nodes", 0, "Количество\u00A0узлов", values_not_shown=[0]),
                NodeStatistParam("edges", 0, "Количество\u00A0соединений", values_not_shown=[0]),
                NodeStatistParam("scale", 1, "Масштаб", values_not_shown=[1], prefix='x'),
                NodeStatistParam("selected", 0, "Выбрано\u00A0узлов", values_not_shown=[0]),
            ]
        }
    

    def add_stat_param(self, param: NodeStatistParam):
        '''Добавляет параметр в панель статистики'''
        if param.key not in self.data.keys():
            self.data[param.key] = param
    

    def update_text(self, attribute: str, value: str) -> None:
        '''Обновляет содержимое панели статистики'''
        if attribute in self.data.keys():
            if self.data[attribute].value == value:
                return
            self.data[attribute].value = value
        else:
            self.data[attribute] = NodeStatistParam(attribute, value)

        self.ref_statistics_text.current.value = self.get_text()
        self.update()

    
    def get_text(self) -> str:
        '''Возвращает текст панели статистики'''
        return '; '.join([
            str(param) for param in self.data.values()
            if param.show_when()
        ])