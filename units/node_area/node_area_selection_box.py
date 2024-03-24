from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node_area import NodeArea

from flet import *
import flet.canvas as cv



class NodeAreaSelectionBox(cv.Canvas):
    """
    Область выделения нод управляемая курсором
    """

    def __init__(
        self,
        page: Page,
        node_area: "NodeArea"
    ):
        super().__init__()
        self.page = page
        self.node_area = node_area

        self.selection_box = self.create_selection_box()
        self.selection_box_stroke = self.create_selection_box_stroke()

        self.shapes = [self.selection_box, self.selection_box_stroke]


    def create_selection_box(self) -> cv.Rect:
        """
        Создает объект области выделения
        """
        return cv.Rect(
            paint = Paint(
                color = colors.with_opacity(0.05, colors.WHITE)
            )
        )
    

    def create_selection_box_stroke(self) -> cv.Path:
        '''
        Обновить обводку прямоугольного выделения
        '''
        self.selection_box_stroke_corner_1 = cv.Path.MoveTo(0, 0)
        self.selection_box_stroke_corner_2 = cv.Path.LineTo(0, 0)
        self.selection_box_stroke_corner_3 = cv.Path.LineTo(0, 0)
        self.selection_box_stroke_corner_4 = cv.Path.LineTo(0, 0)
        return cv.Path(
            [
                self.selection_box_stroke_corner_1,
                self.selection_box_stroke_corner_2,
                self.selection_box_stroke_corner_3,
                self.selection_box_stroke_corner_4,
                cv.Path.Close(),
            ],
            paint = Paint(
                stroke_width = 1,
                color = colors.WHITE,
                style = PaintingStyle.STROKE,
                stroke_dash_pattern = [10, 5],
            ),
        )
        

    def start_selection_box(self, e: DragStartEvent) -> None:
        '''
        Начать выделение
        '''
        self.selection_box.x = e.local_x
        self.selection_box.y = e.local_y
        self.selection_box.width = 0
        self.selection_box.height = 0

        self.selection_box_stroke_corner_1.x = e.local_x
        self.selection_box_stroke_corner_1.y = e.local_y
        self.selection_box_stroke_corner_2.x = e.local_x
        self.selection_box_stroke_corner_2.y = e.local_y
        self.selection_box_stroke_corner_3.x = e.local_x
        self.selection_box_stroke_corner_3.y = e.local_y
        self.selection_box_stroke_corner_4.x = e.local_x
        self.selection_box_stroke_corner_4.y = e.local_y

        self.selection_box.visible = True
        self.selection_box_stroke.visible = True
        self.node_area.clear_selection()

    
    def drag_selection_box(self, e:DragUpdateEvent) -> None:
        '''
        Переместить выделение
        '''
        self.selection_box.width = e.local_x - self.selection_box.x
        self.selection_box.height = e.local_y - self.selection_box.y

        end_x = self.selection_box.x + self.selection_box.width
        end_y = self.selection_box.y + self.selection_box.height

        self.selection_box_stroke_corner_1.x = end_x
        self.selection_box_stroke_corner_2.x = end_x
        self.selection_box_stroke_corner_2.y = end_y
        self.selection_box_stroke_corner_3.y = end_y

        self.update()


    def end_selection_box(self, e: DragEndEvent) -> None:
        '''
        Завершить выделение
        '''
        self.selection_box.visible = False
        self.selection_box_stroke.visible = False
        self.node_area.select_all_in_selection_box(self.selection_box)
        self.update()
    