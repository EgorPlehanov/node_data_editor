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
        self.shapes.append(node_connection.connect_path)
        self.nodes_connects.append(node_connection)

        self.update()
        self.node_area.update_stats(update_edges = True)


    def remove_node_connect(self, node_connection: "NodeConnection") -> None:
        """
        Удалить соединение
        """
        self.shapes.remove(node_connection.connect_path)
        self.nodes_connects.remove(node_connection)

        self.update()
        self.node_area.update_stats(update_edges = True)


    def delete_nodes_connects(self, nodes_to_delete: list["Node"]) -> None:
        '''
        Удаляет соединение между узлами
        '''
        node_to_recalculate = set(
            connect.to_node
            for connect in self.nodes_connects
            if (
                connect.from_node in nodes_to_delete
                and connect.to_node not in nodes_to_delete
            )
        )
        from_nodes_not_delete = set(
            connect.from_node
            for connect in self.nodes_connects
            if (
                connect.from_node not in nodes_to_delete
                and connect.to_node in nodes_to_delete
            )
        )
        for connect in reversed(self.nodes_connects):
            is_delete = False

            if connect.from_node in nodes_to_delete or connect.to_node in nodes_to_delete:
                is_delete = True
                if connect.to_node in node_to_recalculate:
                    connect.to_point.clear_point_on_reconnect(is_recalculate = False)

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