from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from flet import *
import flet.canvas as cv
from typing import Dict

from .node import Node, NodeConfig
from .node_connect_point import NodeConnectPoint



class NodeArea(cv.Canvas):
    def __init__(self, page: Page, workplace: "Workplace"):
        super().__init__()
        self.page = page
        self.workplace = workplace

        self.current_scale = 1
        
        self.background_grid = self.create_background_grid()
        self.shapes = self.background_grid

        self.nodes: list[Node] = []
        self.selected_nodes: list[Node] = []

        self.content = GestureDetector(
            content = Stack(
                width = self.width,
                height = self.height,
                controls = self.nodes,                
            ),
            on_tap = self.clear_selection,
            on_scroll = self.scroll_scale_node_area,
            # on_pan_update = self.drag_all
        )

    
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


    def add_node(self, config: NodeConfig, ref_text_counter: Ref[Text] = None):
        """
        Добавить узел
        """
        node_count = ref_text_counter.current.data
        for _ in range(node_count):
            self.nodes.append(Node(
                page=self.page, node_area=self,
                scale=self.current_scale, config=config
            ))
        self.workplace.node_stats.update_text("nodes", len(self.nodes))
        self.update()

    
    def delete_node(self, node):
        """
        Удалить узел
        """
        self.delete_node_results(node)
        self.delete_node_connect(node)
        self.nodes.remove(node)
        
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
        
        self.workplace.node_stats.update_text("nodes", len(self.nodes))
        self.paint_line()


    def delete_node_connect(self, cur_node: Node):
        '''
        Удаляет соединение между узлами
        '''
        node_to_recalculate = set(
            to_param.node 
            for to_param_list in cur_node.connects_to.values() 
            for to_param in to_param_list
        )

        for to_param_key, from_param in cur_node.connects_from.items():
            if from_param is not None:
                connect_point = cur_node.parameters_dict[to_param_key].connect_point
                connect_point.remove_node_from_connects_to(recalculate_and_paint = False)

        for to_param_list in cur_node.connects_to.values():
            for to_param in reversed(to_param_list):
                to_param.connect_point.remove_node_from_connects_to(recalculate_and_paint = False)

        for node in node_to_recalculate:
            node.calculate()


    def delete_node_results(self, cur_node: Node):
        '''
        Удаляет результаты вычислений узла
        '''
        for view in cur_node.parameters_results_view_dict.values():
            if view is not None:
                self.workplace.result_area.result_controls.remove(view)
        self.workplace.update()


    def calculate_coord(self, point: NodeConnectPoint):
        node = point.node

        left_center = node.width // 2
        top_center = node.height // 2

        point_left = point.left + node.POINT_SIZE // 2 - left_center
        point_top = point.top + node.POINT_SIZE // 2 - top_center

        point_left_scl = point_left * self.current_scale + left_center
        point_top_scl = point_top * self.current_scale + top_center

        return node.left + point_left_scl, node.top + point_top_scl
    

    def paint_line(self, line_len = 10, steepness = 70):
        '''
        Рисует линию соединения
        '''
        line_len *= self.current_scale
        steepness *= self.current_scale
        shp = []
        for node in self.nodes:
            for from_param_key, connects_to_params in node.connects_to.items():
                for param in connects_to_params:
                    from_point: NodeConnectPoint = node.parameters_dict[from_param_key].connect_point
                    to_point: NodeConnectPoint = param.connect_point
                    from_left, from_top = self.calculate_coord(from_point)
                    to_left, to_top = self.calculate_coord(to_point)

                    shp.append(cv.Path(
                        elements = [
                            cv.Path.MoveTo(from_left, from_top),
                            cv.Path.LineTo(from_left + line_len, from_top),
                            cv.Path.CubicTo(
                                from_left + steepness, from_top,
                                to_left - steepness, to_top,
                                to_left - line_len, to_top,
                            ),
                            cv.Path.LineTo(to_left, to_top),
                        ],
                        paint = Paint(
                            stroke_width = 2,
                            style = PaintingStyle.STROKE,
                            color = from_point.point_color
                        ),
                    ))
        
        self.workplace.node_stats.update_text("edges", len(shp))
        
        shp.extend(self.background_grid)
        self.shapes = shp
        self.update()


    def add_selection_node(self, node):
        """
        Добавить выделение
        """
        if node not in self.selected_nodes:
            self.selected_nodes.append(node)
            self.workplace.node_stats.update_text("selected", len(self.selected_nodes))



    def remove_selection_node(self, node):
        """
        Удалить выделение
        """
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
            self.workplace.node_stats.update_text("selected", len(self.selected_nodes))


    def clear_selection(self, e):
        """
        Очистить выделение со всех выбранных узлов
        """
        for node in reversed(self.selected_nodes):
            node.toggle_selection(None)
        self.selected_nodes = []


    def drag_selection(self, top_delta = 0, left_delta = 0):
        """
        Переместить выделение
        """
        for node in self.selected_nodes:
            node.drag_node(left_delta, top_delta)


    def drag_all(self, e):
        '''
        Переместить все узлы
        '''
        for node in self.nodes:
            node.drag_node(e.delta_x, e.delta_y)
        self.paint_line()
    

    def select_all(self, e):
        '''
        Выделить все узлы
        '''
        for node in self.nodes:
            if not node.is_selected:
                node.toggle_selection(None)


    def delete_selected_nodes(self, e):
        '''
        Удалить выделенные узлы
        '''
        for node in reversed(self.selected_nodes):
            self.delete_node(node)
        

    def invert_selection(self, e):
        '''
        Инвертировать выделение
        '''
        for node in self.nodes:
            node.is_selected = not node.is_selected
            node.set_selection()
        self.update()


    def move_selection_to_start(self, e):
        '''
        Переместить выделенные узлы в начало
        '''
        for idx, node in enumerate(sorted(self.selected_nodes, key=lambda x: x.id)):
            node.top = idx * 30
            node.left = (idx % 5) * 100
        self.paint_line()
    

    def scroll_scale_node_area(self, e: ScrollEvent):
        '''
        Масштабирование узлов
        '''
        scale_min, scale_max, scale_round = 0.1, 2, 2

        scale_delta = round(e.scroll_delta_y / -2000, scale_round)
        new_scale = round(self.current_scale + scale_delta, scale_round)
        if (new_scale < scale_min or new_scale > scale_max):
            return
        
        self.current_scale = new_scale
        self.set_scale(e.local_x, e.local_y, scale_delta)

        self.workplace.node_stats.update_text("scale", self.current_scale)
        self.update()


    def set_scale(self, zoom_x, zoom_y, scale_delta):
        '''
        Установить масштаб узлов
        '''
        for node in self.nodes:
            node.scale = self.current_scale
            
            l_x = (node.left + node.width // 2) - zoom_x
            l_y = (node.top + node.height // 2) - zoom_y

            node.drag_node(
                l_x * scale_delta / self.current_scale,
                l_y * scale_delta / self.current_scale
            )
            self.paint_line()


    def get_node_parameter(self, node_id: int, param_id: int):
        """
        Возвращает параметр узла
        """
        node = next(node for node in self.nodes if node.id == node_id)
        return next(param for param in node.parameters_dict.values() if param.id == param_id)