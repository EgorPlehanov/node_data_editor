from .result_area import ResultArea
from .node_area import NodeArea
from .statistics_panel import StatisticsPanel
from .menubar.menubar import FunctionMenuBar

from flet import *
from typing import List



class Workplace(Column):
    """
    Рабочая область приложения
    """

    def __init__(
        self,
        app,    # Может быть переданно при интеграции с другим приложением
        page: Page
    ):
        super().__init__()
        self.app = app
        self.page = page

        self.spacing = 0
        self.expand = True

        self.menubar = FunctionMenuBar(page, self)
        self.result_area = ResultArea(page, self)
        self.node_stats = StatisticsPanel(page, self)
        self.node_area = NodeArea(page, self)

        self.controls = self.create_controls()

        self.is_divider_dragging = False


    def create_controls(self) -> List[Container]:
        """
        Создает элементы рабочей области
        """
        self.ref_node_area_container = Ref[Container]()
        self.ref_result_area_container = Ref[Container]()

        menubar_container = Container(
            Row([self.menubar]),
            # bgcolor=colors.GREY_900,
        )
        node_area_container = Container(
            ref = self.ref_node_area_container,
            content = Column(
                controls = [
                    Container(self.node_area, expand=True),
                    Container(
                        self.node_stats,
                        bgcolor = "#111111",
                        padding = 5,
                    ),
                ],
                spacing = 0,
            ),
            expand = 3,
            bgcolor = colors.BLACK38,
        )
        vertical_divider = GestureDetector(
            content = VerticalDivider(
                thickness = 5,
                width = 5,
                color = colors.GREY_900,
            ),
            mouse_cursor = MouseCursor.RESIZE_COLUMN,
            drag_interval = 20,
            on_enter = self.hover_divider,
            on_exit = self.hover_exit_divider,
            on_horizontal_drag_start = self.drag_start_divider,
            on_horizontal_drag_update = self.resize_columns,
            on_horizontal_drag_end = self.drag_end_divider
        )
        result_area_container = Container(
            ref = self.ref_result_area_container,
            content = self.result_area,
            bgcolor = colors.GREY_900,
            expand = 1,
        )
        return [
            menubar_container,
            Container(
                content = Row(
                    controls = [
                        node_area_container,
                        vertical_divider,
                        result_area_container
                    ],
                    spacing = 0,
                    expand = True,
                ),
                expand = True,
                bgcolor = colors.GREY_900,
            )
        ]
    
    
    def resize_columns(self, e: DragUpdateEvent) -> None:
        '''
        Изменяет ширину колонок
        '''
        node_area_width = int(e.global_x)
        node_area_width = max(node_area_width, 1)

        result_area_width = int(self.page.width - node_area_width)
        result_area_width = max(result_area_width, 0)

        self.ref_node_area_container.current.expand = node_area_width
        self.ref_result_area_container.current.expand = result_area_width

        self.hover_divider(e)


    def hover_divider(self, e: HoverEvent) -> None:
        '''
        Изменяет цвет вертикального разделителя, когда курсор наводится на вертикальный разделитель
        '''
        e.control.content.color = colors.DEEP_ORANGE_ACCENT_400
        self.update()
    

    def hover_exit_divider(self, e: HoverEvent) -> None:
        '''
        Изменяет цвет вертикального разделителя, когда курсор убирается с вертикального разделителя
        '''
        if self.is_divider_dragging:
            return
        e.control.content.color = colors.GREY_900
        self.update()

    
    def drag_start_divider(self, e: DragStartEvent) -> None:
        """
        Включает режим перетаскивания вертикального разделителя
        """
        self.is_divider_dragging = True


    def drag_end_divider(self, e: DragEndEvent) -> None:
        """
        Отключает режим перетаскивания вертикального разделителя
        """
        self.is_divider_dragging = False
        self.hover_exit_divider(e)
