from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node_area import NodeArea

from flet import *
import flet.canvas as cv 



class NodeAreaBackgroundGrid(cv.Canvas):
    """
    Фоновая сетка c точками в рабочей области с нодами
    """

    def __init__(
        self,
        page: Page,
        node_area: "NodeArea"
    ):
        super().__init__()
        self.page = page
        self.node_area = node_area

        self.shapes = self.create_background_grid()


    def create_background_grid(self):
        '''
        Создает фоновую сетку
        '''
        return [
            cv.Line(
                0, i * 50 + 1,
                5000, i * 50 + 1,
                paint = Paint(
                    color = colors.WHITE12,
                    stroke_width = 2,
                    stroke_dash_pattern = [2, 50],
                )
            )
            for i in range(0, 20)
        ]
