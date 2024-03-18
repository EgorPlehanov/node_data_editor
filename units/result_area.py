from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .workplace import Workplace
    from .node.node_result_view import NodeResultView

from flet import *
from flet_core.scrollable_control import ScrollableControl



class ResultArea(Container):
    def __init__(self, page: Page, workplace: "Workplace"):
        super().__init__()

        self.page = page
        self.workplace = workplace
        
        self.expand = True
        self.alignment = alignment.top_center
        self.bgcolor = colors.GREY_900

        self.result_controls = []
        self.content = self.create_controls()


    def create_controls(self):
        self.ref_result_view = Ref[Column]()
        return Column(
            tight = True,
            expand = True,
            scroll = ScrollMode.AUTO,
            controls = [Container(
                padding = 10,
                content = Column(
                    ref = self.ref_result_view,
                    controls = self.result_controls,
                    spacing = 10,
                )
            )]
        )
    

    def change_results_positions(self, from_result: "NodeResultView", to_result: "NodeResultView") -> None:
        '''Перемещает карточку функций в списке карточек функции и в списке результатов'''
        from_index = self.result_controls.index(from_result)
        to_index = self.result_controls.index(to_result)

        to_result.set_default_color()
        
        # Перемещает элемент с индексом from_index в положениие to_index
        self.result_controls.insert(to_index, self.result_controls.pop(from_index))

        # Меняет местами 2 элемента в списке
        # self.result_controls[to_index], self.result_controls[from_index] = self.result_controls[from_index], self.result_controls[to_index]
        
        self._scroll_view_to(from_result.key)
        self.update()


    def _scroll_view_to(self, key: str | int, view: ScrollableControl = None) -> None:
        '''
        Прокручивает вью до элемента с заданным ключом
        '''
        if view is None:
            view = self.ref_result_view.current
        view.scroll_to(
            key = str(key),
            duration = 500,
            curve = animation.AnimationCurve.FAST_OUT_SLOWIN
        )
    
    