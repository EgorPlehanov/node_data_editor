from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..workplace import Workplace

from .node_area_background_grid import NodeAreaBackgroundGrid
from .node_area_selection_box import NodeAreaSelectionBox
from .node_area_connections import NodeAreaConnections
from ..node import Node, NodeConfig, NodeConnection
from ..result_area import ResultArea
from ..statistics_panel import StatisticsPanel

from flet import *
import flet.canvas as cv
from typing import Union, List, Dict
from collections import defaultdict, deque



class NodeArea(GestureDetector):
    """
    Область работы с нодами
    """

    def __init__(
        self,
        page: Page,
        workplace: "Workplace"
    ):
        super().__init__()
        self.page: Page = page
        self.workplace: "Workplace" = workplace
        self.node_area_statistics: "StatisticsPanel" = self.workplace.node_stats
        self.result_area: "ResultArea" = self.workplace.result_area

        self.setup_values()

        self.content = self.create_content()


    def create_content(self):
        """
        Создает содержимое
        """
        return Stack([
            self.canvas_background_grid,
            self.canvas_connections,
            self.stack_nodes,
            self.canvas_selection_box,
        ])
    

    def setup_values(self):
        """
        Устанавливает значения по умолчанию
        """
        self.current_scale = 1

        self.nodes: list[Node] = []
        self.selected_nodes: list[Node] = []
        self.nodes_connects: List[NodeConnection] = []
        self.canvas_connections_shapes: List[cv.Path] = []

        self.canvas_background_grid = NodeAreaBackgroundGrid(self.page, self)
        self.canvas_connections = NodeAreaConnections(
            self.page, self, self.nodes_connects, self.canvas_connections_shapes, 
        )
        self.stack_nodes = Stack(self.nodes)
        self.canvas_selection_box = NodeAreaSelectionBox(self.page, self)

        self.drag_interval = 20
        self.on_tap = lambda e: self.clear_selection()
        self.on_scroll = self.scroll_scale_node_area
        self.on_pan_start = self.canvas_selection_box.start_selection_box
        self.on_pan_update = self.canvas_selection_box.drag_selection_box
        self.on_pan_end = self.canvas_selection_box.end_selection_box


    def update_stats(
        self,
        update_all: bool = False,
        update_nodes: bool = False,
        update_selected: bool = False,
        update_scale: bool = False,
        update_edges: bool = False,
        cycles: List[List[Node]] = None
    ):
        """
        Обновить статистику
        """
        if update_nodes or update_all:
            self.node_area_statistics.update_text("nodes", len(self.nodes))
        if update_selected or update_all:
            self.node_area_statistics.update_text("selected", len(self.selected_nodes))
        if update_scale or update_all:
            self.node_area_statistics.update_text("scale", self.current_scale)
        if update_edges or update_all:
            self.node_area_statistics.update_text("edges", len(self.nodes_connects))
        if cycles is not None or update_all:
            if update_all:
                cycles = self.find_cycles()
            self.node_area_statistics.update_text("cycles", cycles)


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
        self.stack_nodes.update()
        self.update_stats(update_nodes = True)

    
    def delete_node(self, nodes_to_delete: Union[List[Node], Node]):
        """
        Удалить узел
        """
        if not isinstance(nodes_to_delete, list):
            nodes_to_delete = [nodes_to_delete]

        self.canvas_connections.delete_nodes_connects(nodes_to_delete)

        for node in reversed(nodes_to_delete):
            # Удаляем результат
            if node.is_display_result:
                self.result_area.delete_node_results(node)

            # Удаляем из списка выделенных
            if node.is_selected:
                self.selected_nodes.remove(node)

            self.nodes.remove(node)
        
        self.workplace.result_area.update()
        self.stack_nodes.update()
        self.canvas_connections.update_connects_lines()
        self.update_stats(update_all = True)


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
        self.stack_nodes.update()


    def drag_selection(self, top_delta = 0, left_delta = 0):
        """
        Переместить выделение
        """
        for node in self.selected_nodes:
            node.drag_node(left_delta, top_delta)

        self.stack_nodes.update()
        self.canvas_connections.update_connects_lines()


    def drag_all(self, e):
        '''
        Переместить все узлы
        '''
        for node in self.nodes:
            node.drag_node(e.delta_x, e.delta_y)

        self.stack_nodes.update()
        self.canvas_connections.update_connects_lines()
    

    def select_all(self):
        '''
        Выделить все узлы
        '''
        for node in self.nodes:
            if not node.is_selected:
                node.toggle_selection(is_update=False)
        self.stack_nodes.update()


    def delete_selected_nodes(self):
        '''
        Удалить выделенные узлы
        '''
        self.delete_node(self.selected_nodes)
        

    def invert_selection(self):
        '''
        Инвертировать выделение
        '''
        for node in self.nodes:
            node.toggle_selection(is_update = False)
        self.stack_nodes.update()


    def move_selection_to_start(self):
        '''
        Переместить выделенные узлы в начало
        '''
        for idx, node in enumerate(sorted(self.selected_nodes, key=lambda x: x.id)):
            node.top = idx * 30
            node.left = (idx % 5) * 100
        self.stack_nodes.update()
        self.canvas_connections.update_connects_lines()
    

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

        self.stack_nodes.update()
        self.canvas_connections.update_connects_lines()
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


    def select_all_in_selection_box(self, selection_box: cv.Rect):
        '''
        Выделить все узлы в выделенном прямоугольнике
        '''
        x_start = selection_box.x
        y_start = selection_box.y
        x_end = x_start + selection_box.width
        y_end = y_start + selection_box.height

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

        self.stack_nodes.update()
    

    def recalculate_dependent_nodes(self, start_node: List[Node] = None):
        '''
        Пересчитывает зависимые узлы или все если start_node не указан
        '''
        recalculate_node_queue: List[Node] = (
            self.topological_sort_all(node)
            if start_node is None
            else self.topological_sort_from_node(start_node)
        )
        
        cycles = self.find_cycles()
        self.update_stats(cycles=cycles)
        if len(cycles) != 0:
            return
        
        for node in recalculate_node_queue:
            node.calculate(is_recalculate_dependent_nodes=False)


    def get_graph(self) -> Dict[Node, List[Node]]:
        """
        Функция для создания графа из списка связей
        """
        graph = {}
        for connect in self.nodes_connects:
            if connect.from_node not in graph:
                graph[connect.from_node] = []
            graph[connect.from_node].append(connect.to_node)
        return graph


    def topological_sort_from_node(self, start_node) -> List[Node]:
        """
        Выполняет топологическую сортировку для заданного исходного узла
        Возвращает список узлов в топологическом порядке начиная со следающего после start_node
        """
        graph = self.get_graph()

        if self.has_cycle(graph, start_node):
            return None

        # Функция для рекурсивной топологической сортировки
        def dfs(node, visited, result):
            visited.add(node)
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        dfs(neighbor, visited, result)
            result.append(node)

        result = []
        visited = set()
        dfs(start_node, visited, result)

        return result[::-1][1:]
    

    def topological_sort_all(self) -> List[Node]:
        """
        Выполняет топологическую сортировку алгоритм Кана для определения
        оптимального порядка обновления функций для всех узлов в графе 
        """
        # Инициализация словаря для хранения входящих рёбер для каждого узла
        in_degree = defaultdict(int)
        # Инициализация словаря для хранения списка смежных узлов для каждого узла
        graph = defaultdict(list)
        
        # Заполнение словарей на основе связей
        for connect in self.nodes_connects:
            graph[connect.from_node].append(connect.to_node)
            in_degree[connect.to_node] += 1
        
        # Инициализация списка узлов без входящих рёбер
        zero_in_degree_nodes = deque([node for node in graph if in_degree[node] == 0])
        
        # Процесс топологической сортировки
        result = []
        while zero_in_degree_nodes:
            node = zero_in_degree_nodes.popleft()
            result.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    zero_in_degree_nodes.append(neighbor)
        
        # Проверка наличия цикла
        if len(result) != len(graph):
            return None  # Граф содержит цикл
        else:
            return result  # Топологическая сортировка выполнена успешно
        

    def has_cycle(self, graph: Dict[Node, List[Node]] = None, start_node: Node = None) -> bool:
        """
        Проверяет наличие циклов в графе с использованием алгоритма поиска в глубину (DFS).
        """
        # Функция для поиска циклов
        def dfs(node):
            if node in on_path:
                return True
            if node in visited:
                return False

            visited.add(node)
            on_path.add(node)

            if node in graph:
                for neighbor in graph[node]:
                    if dfs(neighbor):
                        return True

            on_path.remove(node)
            return False

        if graph is None:
            graph = self.get_graph()

        # Маркеры для отслеживания посещенных узлов и узлов на текущем пути
        visited = set()
        on_path = set()

        # Запускаем поиск в глубину из каждого узла графа
        if start_node is None:
            for node in graph:
                if dfs(node):
                    return True
        else:
            if dfs(start_node):
                return True

        return False
    

    def find_cycles(self, graph: Dict[Node, List[Node]] = None) -> List[List[Node]]:
        """
        Функция для поиска всех циклов в графе
        """
        if graph is None:
            graph = self.get_graph()

        def dfs(node, visited, current_path):
            visited[node] = True
            current_path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in current_path:
                        if neighbor not in visited:
                            dfs(neighbor, visited, current_path)
                    else:
                        index = current_path.index(neighbor)
                        cycle = current_path[index:]
                        cycles.append(cycle)
            
            current_path.pop()
        
        cycles = []
        visited = {}
        for node in graph:
            if node not in visited:
                dfs(node, visited, [])
        return cycles