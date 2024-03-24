from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node_area import NodeArea
    from ..node.node import Node
    from ..node import NodeConnection

from flet import *
import flet.canvas as cv
from typing import List



class NodeAreaConnections(cv.Canvas):
    """
    Облисть отрисовки линий соединений нод
    """

    def __init__(
        self,
        page: Page,
        node_area: 'NodeArea',
        nodes_connects:  List["NodeConnection"],
        connections_shapes: List[cv.Path]
    ):
        super().__init__()
        self.page = page
        self.node_area = node_area
        self.nodes_connects = nodes_connects
        self.shapes = connections_shapes


    def add_node_connect(self, node_connection: "NodeConnection") -> None:
        """
        Добавить соединение
        """
        self.add_node_from_to_connect(node_connection)

        self.shapes.append(node_connection.connect_path)
        self.nodes_connects.append(node_connection)

        self.update()
        self.node_area.update_stats(update_edges = True)


    def add_node_from_to_connect(self, node_connection: "NodeConnection") -> None:
        """
        Добавить соединение в словари ноды
        """
        node_connection.from_node.add_connect_to(node_connection.from_param, node_connection.to_param)
        node_connection.to_node.add_connect_from(node_connection.from_param,  node_connection.to_param)

    
    def remove_node_connect(self, node_connection: "NodeConnection") -> None:
        """
        Удалить соединение
        """
        self.remove_node_from_to_connect(node_connection)

        self.shapes.remove(node_connection.connect_path)
        self.nodes_connects.remove(node_connection)

        self.update()
        self.node_area.update_stats(update_edges = True)


    def remove_node_from_to_connect(self, node_connection: "NodeConnection") -> None:
        """
        Удалить соединение из словарей ноды
        """
        from_node = node_connection.from_node
        to_node = node_connection.to_node
        from_node.remove_connect_to(node_connection.from_param, node_connection.to_param)
        to_node.remove_connect_from(node_connection.to_param)


    def delete_nodes_connects(self, nodes_to_delete: list["Node"]) -> None:
        '''
        Удаляет соединение между узлами
        '''
        node_to_recalculate = set(
            to_param.node
            for node in nodes_to_delete
            for to_params_list in node.connects_to.values()
            for to_param in to_params_list
            if to_param.node not in nodes_to_delete
        )
        from_nodes_not_delete = set(
            from_param.node
            for node in nodes_to_delete
            for from_param in node.connects_from.values()
            if (
                from_param is not None
                and from_param.node not in nodes_to_delete
            )
        )
        for connect in reversed(self.nodes_connects):
            is_delete = False

            if connect.from_node in nodes_to_delete:
                is_delete = True
                if connect.to_node in node_to_recalculate:
                    connect.to_node.remove_connect_from(connect.from_param)
                    connect.to_point.clear_point_on_reconnect(is_recalculate = False)
                
            if connect.to_node in nodes_to_delete:
                is_delete = True
                if connect.from_node in from_nodes_not_delete:
                    connect.from_node.remove_connect_to(connect.from_param, connect.to_param)
                    connect.from_point.clear_point_on_reconnect(is_recalculate = False)

            if is_delete:
                self.shapes.remove(connect.connect_path)
                self.nodes_connects.remove(connect)

        for node in node_to_recalculate:
            node.calculate()


    def update_connects_lines(self, selected_only = False):
        '''
        Рисует линию соединения
        '''
        # TODO: Реализовать отрисовку линий соединений только для выделенных узлов
        # print(f"[{', '.join(str(node) for node in self.nodes_connects)}]") # DEBUG
        for connect in self.nodes_connects:
            connect.update_connect_path()

        self.update()