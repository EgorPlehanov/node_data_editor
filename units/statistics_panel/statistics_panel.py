from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from .statistic_parameter import StatisticParameter

from flet import *
from typing import Dict, List



class StatisticsPanel(Row):
    """
    Панель статистики
    """
    
    def __init__(
        self,
        page: Page,
        workplace: "Workplace"
    ):
        super().__init__()
        self.page = page
        self.workplace = workplace

        self.data: Dict[str, StatisticParameter] = self.create_statistics_data()
        self.controls = self.create_controls()
    

    def create_statistics_data(self) -> Dict[str, StatisticParameter]:
        '''
        Создает словарь с данными о параметрах для панели статистики
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
                StatisticParameter("nodes", 0, "Узлов", values_not_shown=[0]),
                StatisticParameter("edges", 0, "Соединений", values_not_shown=[0]),
                StatisticParameter("scale", 1, "Масштаб", values_not_shown=[1], prefix='x'),
                StatisticParameter("selected", 0, "Выбрано", values_not_shown=[0]),
                StatisticParameter(
                    "cycles", [], "Циклов", values_not_shown=[[]],
                    tooltip = "Функции не могут быть пересчитаны пока есть циклы",
                    to_string = cycles_to_string, text_color=colors.RED,
                    bgcolor = colors.with_opacity(0.1, colors.RED_300),
                ),
            ]
        }


    def create_controls(self) -> List[Control]:
        """
        Создает список контролов для панели статистики
        """
        return [stat_param for stat_param in self.data.values()]


    def add_stat_param(self, param: StatisticParameter) -> None:
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