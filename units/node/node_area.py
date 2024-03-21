from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from flet import *
import flet.canvas as cv
from typing import Dict, List, Set

from .node import Node, NodeConfig
from .node_connect_point import NodeConnectPoint
from .node_connection import NodeConnection



class NodeArea(GestureDetector):
    def __init__(self, page: Page, workplace: "Workplace"):
        super().__init__()
        self.page = page
        self.workplace = workplace

        self.setup_values()

        self.content = self.create_content()
        

    def create_content(self):
        """
        Создает содержимое
        """
        self.canvas_background_grid = cv.Canvas(shapes = self.background_grid)
        self.canvas_connections = cv.Canvas(self.canvas_connections_shapes)
        self.stack_nodes = Stack(self.nodes)
        self.canvas_selection_box = cv.Canvas([self.selection_box, self.selection_box_stroke])
        return Stack([
            self.canvas_background_grid,
            self.canvas_connections,
            self.stack_nodes,
            self.canvas_selection_box,
        ])

    
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
    

    def setup_values(self):
        """
        Устанавливает значения по умолчанию
        """
        self.current_scale = 1

        self.nodes: list[Node] = []
        self.selected_nodes: list[Node] = []
        self.nodes_connects: List[NodeConnection] = []
        self.canvas_connections_shapes: List[cv.Path] = []
        
        self.background_grid = self.create_background_grid()

        self.selection_box = self.create_selection_box()
        self.selection_box_stroke = self.create_selection_box_stroke()

        self.drag_interval = 20
        self.on_tap = lambda e: self.clear_selection()
        self.on_scroll = self.scroll_scale_node_area
        self.on_pan_start = self.start_selection_box
        self.on_pan_update = self.drag_selection_box
        self.on_pan_end = self.end_selection_box


    def add_node_connect(self, node_connection: NodeConnection):
        """
        Добавить соединение
        """
        self.add_node_from_to_connect(node_connection)

        self.canvas_connections_shapes.append(node_connection.connect_path)
        self.nodes_connects.append(node_connection)

        self.canvas_connections.update()
        self.update_stats(update_edges = True)


    def add_node_from_to_connect(self, node_connection: NodeConnection):
        """
        Добавить соединение в словари ноды
        """
        from_node = node_connection.from_node
        to_node = node_connection.to_node
        from_node.add_connect_to(node_connection.from_param, node_connection.to_param)
        to_node.add_connect_from(node_connection.from_param,  node_connection.to_param)

    
    def remove_node_connect(self, node_connection: NodeConnection):
        """
        Удалить соединение
        """
        self.remove_node_from_to_connect(node_connection)

        self.canvas_connections_shapes.remove(node_connection.connect_path)
        self.nodes_connects.remove(node_connection)

        self.canvas_connections.update()
        self.update_stats(update_edges = True)


    def remove_node_from_to_connect(self, node_connection: NodeConnection):
        """
        Удалить соединение из словарей ноды
        """
        from_node = node_connection.from_node
        to_node = node_connection.to_node
        from_node.remove_connect_to(node_connection.from_param, node_connection.to_param)
        to_node.remove_connect_from(node_connection.to_param)


    def update_stats(self,
        update_all = False,
        update_nodes = False,
        update_selected = False,
        update_scale = False,
        update_edges = False
    ):
        """
        Обновить статистику
        """
        if update_nodes or update_all:
            self.workplace.node_stats.update_text("nodes", len(self.nodes))
        if update_selected or update_all:
            self.workplace.node_stats.update_text("selected", len(self.selected_nodes))
        if update_scale or update_all:
            self.workplace.node_stats.update_text("scale", self.current_scale)
        if update_edges or update_all:
            self.workplace.node_stats.update_text("edges", len(self.nodes_connects))


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
        self.update_stats(update_nodes = True)

    
    def delete_node(self, node):
        """
        Удалить узел
        """
        self.delete_node_results(node)
        # self.delete_node_connect(node) # TODO: ИСПРАВИТЬ 
        self.nodes.remove(node)
        
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
        
        self.paint_line()
        self.workplace.result_area.update()
        self.workplace.node_stats.update_text("nodes", len(self.nodes))
        self.update_stats(update_all = True)


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
            self.update_stats(update_selected = True)


    def remove_selection_node(self, node):
        """
        Удалить выделение
        """
        if node in self.selected_nodes:
            self.selected_nodes.remove(node)
            self.update_stats(update_selected = True)


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
        self.paint_line()


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
        self.update_stats(update_scale = True)


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

        self.canvas_selection_box.update()


    def end_selection_box(self, e):
        '''
        Завершить выделение
        '''
        self.selection_box.visible = False
        self.selection_box_stroke.visible = False
        self.select_all_in_selection_box()
        self.canvas_selection_box.update()
        self.stack_nodes.update()


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


    def paint_line(self, selected_only = False):
        '''
        Рисует линию соединения
        '''
        print(len(self.nodes_connects))
        print(*self.nodes_connects)
        for connect in self.nodes_connects:
            connect.update_connect_path()

        self.canvas_connections.update()
        self.stack_nodes.update()
    

    def create_nodes_connects(self, selected_only: bool = False) -> List[NodeConnection]:
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
            NodeConnection(self, node.parameters_dict[from_param_key], to_param)
            for from_param_key, connects_to_params in node.connects_to.items()
            for to_param in connects_to_params
        }


    def _get_node_connects_from(self, node: Node) -> Set[NodeConnection]:
        """
        Возвращает список соединений входящих в узел
        """
        return {
            NodeConnection(self, from_param, node.parameters_dict[to_param_key])
            for to_param_key, from_param in node.connects_from.items()
            if from_param is not None
        }
    

    def update_connects_lines(self, nodes_to_update: List[Node]):
        '''
        Обновляет линии соединений
        '''
        pass


    def drag_connects_lines(self, delta_x: int, delta_y: int, nodes_to_update: List[NodeConnection] = None):
        '''
        Перетаскивает линии соединений
        '''
        if nodes_to_update is None:
            nodes_to_update = self.nodes_connects
        for node in nodes_to_update:
            node.drag_connect_path(delta_x, delta_y)
    