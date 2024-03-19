from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from flet import *
import flet.canvas as cv
from typing import Dict, List, Set

from .node import Node, NodeConfig
from .node_connect_point import NodeConnectPoint
from .node_typing import NodeConnection



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

        self.selection_box = self.create_selection_box()
        self.selection_box_stroke = self.create_selection_box_stroke()

        self.content = GestureDetector(
            content = Stack([
                Stack(self.nodes),
                cv.Canvas([
                    self.selection_box,
                    self.selection_box_stroke
                ]),
            ]),
            drag_interval = 20,
            on_tap = lambda e: self.clear_selection(),
            on_scroll = self.scroll_scale_node_area,
            on_pan_start = self.start_selection_box,
            on_pan_update = self.drag_selection_box,
            on_pan_end = self.end_selection_box,
        )

        self.nodes_connects = self.get_nodes_connects()

    
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
        self.update()
        self.workplace.node_stats.update_text("nodes", len(self.nodes))

    
    def delete_node(self, node):
        """
        Удалить узел
        """
        self.delete_node_results(node)
        self.delete_node_connect(node)
        self.nodes.remove(node)
        
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
        
        self.paint_line()
        self.workplace.result_area.update()
        self.workplace.node_stats.update_text("nodes", len(self.nodes))


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


    def clear_selection(self):
        """
        Очистить выделение со всех выбранных узлов
        """
        for node in reversed(self.selected_nodes):
            node.toggle_selection(is_update=False)
        self.selected_nodes = []
        self.update()


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
    

    def select_all(self):
        '''
        Выделить все узлы
        '''
        for node in self.nodes:
            if not node.is_selected:
                node.toggle_selection(is_update=False)
        self.update()


    def delete_selected_nodes(self):
        '''
        Удалить выделенные узлы
        '''
        for node in reversed(self.selected_nodes):
            self.delete_node(node)
        

    def invert_selection(self):
        '''
        Инвертировать выделение
        '''
        for node in self.nodes:
            node.toggle_selection(is_update = False)
        self.update()


    def move_selection_to_start(self):
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

        self.paint_line()
        self.workplace.node_stats.update_text("scale", self.current_scale)


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


    def get_node_parameter(self, node_id: int, param_id: int):
        """
        Возвращает параметр узла
        """
        node = next(node for node in self.nodes if node.id == node_id)
        return next(param for param in node.parameters_dict.values() if param.id == param_id)
    

    def create_selection_box(self):
        """
        Создает объект области выделения
        """
        return cv.Rect(
            paint = Paint(
                color = colors.with_opacity(0.05, colors.WHITE)
            )
        )
    

    def create_selection_box_stroke(self):
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
        

    def start_selection_box(self, e):
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
        self.clear_selection()

    
    def drag_selection_box(self, e):
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


    def end_selection_box(self, e):
        '''
        Завершить выделение
        '''
        self.selection_box.visible = False
        self.selection_box_stroke.visible = False
        self.select_all_in_selection_box()
        self.update()


    def select_all_in_selection_box(self):
        '''
        Выделить все узлы в выделенном прямоугольнике
        '''
        x_start = self.selection_box.x
        y_start = self.selection_box.y
        x_end = x_start + self.selection_box.width
        y_end = y_start + self.selection_box.height

        x_start, x_end = min(x_start, x_end), max(x_start, x_end)
        y_start, y_end = min(y_start, y_end), max(y_start, y_end)

        for node in self.nodes:
            if (
                node.left < x_end
                and node.top < y_end
                and node.left + node.width > x_start
                and node.top + node.height > y_start
            ):
                if not node.is_selected:
                    node.toggle_selection(is_update=False)


    def calculate_coord(self, point: NodeConnectPoint):
        node = point.node

        left_center = node.width // 2
        top_center = node.height // 2

        point_left = point.left + node.POINT_SIZE // 2 - left_center
        point_top = point.top + node.POINT_SIZE // 2 - top_center

        point_left_scl = point_left * self.current_scale + left_center
        point_top_scl = point_top * self.current_scale + top_center

        return node.left + point_left_scl, node.top + point_top_scl
    

    def __paint_line(self, line_len = 10, steepness = 70):
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
        edges_count = len(shp)
        shp.extend(self.background_grid)
        self.shapes = shp

        self.update()
        self.workplace.node_stats.update_text("edges", edges_count)


    def paint_line(self, selected_only = False, line_len = 10, steepness = 70):
        '''
        Рисует линию соединения
        '''
        line_len *= self.current_scale
        steepness *= self.current_scale
        shp = []

        for connect in self.get_nodes_connects(selected_only):
            from_left, from_top = self.calculate_coord(connect.from_point)
            to_left, to_top = self.calculate_coord(connect.to_point)

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
                    color = connect.from_point.point_color
                ),
            ))

        edges_count = len(shp)
        shp.extend(self.background_grid)
        self.shapes = shp

        self.update()
        self.workplace.node_stats.update_text("edges", edges_count)
    

    def get_nodes_connects(self, selected_only: bool = False) -> List[NodeConnection]:
        '''
        Возвращает список соединений
        '''
        unique_connects: Set[NodeConnection] = set()
        for node in self.nodes:
            if selected_only and not node.is_selected:
                continue
            unique_connects.update(self._get_node_connects_to(node))
            if selected_only:
                unique_connects.update(self._get_node_connects_from(node))
        return list(unique_connects)
    

    def _get_node_connects_to(self, node: Node) -> Set[NodeConnection]:
        """
        Возвращает список соединений исходящих из узла
        """
        return {
            NodeConnection(node.parameters_dict[from_param_key], to_param)
            for from_param_key, connects_to_params in node.connects_to.items()
            for to_param in connects_to_params
        }


    def _get_node_connects_from(self, node: Node) -> Set[NodeConnection]:
        """
        Возвращает список соединений входящих в узел
        """
        return {
            NodeConnection(from_param, node.parameters_dict[to_param_key])
            for to_param_key, from_param in node.connects_from.items()
            if from_param is not None
        }
    