from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node import Node
    from ..result_area import ResultArea

from flet import *
from flet.matplotlib_chart import MatplotlibChart
from flet.plotly_chart import PlotlyChart
import cv2
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .calculate_function.calculate_function_typing import *



class NodeResultView(DragTarget):
    '''
    Виджет для отображения результата вычисления узла
    '''
    def __init__(self, node: "Node", result_area: "ResultArea", result_dict: dict = {}):
        super().__init__()
        self.node = node
        self.result_area = result_area
        self.result_dict = result_dict

        self.set_style()

        self.content = self._create_content()

        self.on_will_accept = self.will_drag_accept
        self.on_accept = self.drag_accept
        self.on_leave = self.drag_leave


    def set_style(self):
        '''
        Устанавливает стиль
        '''
        self.set_result_value()

        self.id = self.node.id
        self.key = self.id
        self.group = "result"


    def set_result_value(self):
        """
        Устанавливает значение результата
        """
        self.current_time = self.result_dict.get("current_time", None) if self.result_dict is not None else None
        self.label = self.result_dict.get("label", None) if self.result_dict is not None else None
        self.result: NodeResult = self.result_dict.get("result", None) if self.result_dict is not None else None
        self.result_type = self.result.type if isinstance(self.result, NodeResult) else ResultType.NONE
        self.result_value = self.result.value if isinstance(self.result, NodeResult) else None


    def drag_accept(self, e: DragTargetAcceptEvent):
        '''Перемещает карточку (срабатывает при подтверждении перетаскивания)'''
        src: Container = self.page.get_control(e.src_id)
        from_result = src.content.data
        to_result = self
        if from_result == to_result:
            self.set_default_color()
            return
        
        self.result_area.change_results_positions(from_result, to_result)


    def will_drag_accept(self, e: ControlEvent):
        '''Срабатывает при наведении курсора с перетаскиваемой карточкой на эту карточку'''
        self.ref_card_conteiner.current.bgcolor = colors.GREEN_500 if e.data == "true" else colors.RED_500
        self.update()


    def drag_leave(self, e: ControlEvent):
        '''Срабатывает при отмене перетаскивания карточки'''
        self.set_default_color()


    def set_default_color(self):
        self.ref_card_conteiner.current.bgcolor = colors.BLACK26
        self.update()
    

    def update_result(self, result_dict: dict):
        """
        Обновляет содержимое
        """
        self.result_dict = result_dict
        self.set_result_value()
        self.content = self._create_content()


    def _create_content(self):
        '''
        Создает содержимое
        '''
        value_type_to_view = {
            ResultType.NONE:            self.create_none_view_element,
            ResultType.STR_VALUE:       self.create_str_view_element,
            ResultType.NUMBER_VALUE:    self.crate_num_view_element,
            ResultType.IMAGE_CV2:       self.crate_image_cv2_view_element,
            ResultType.IMAGE_BASE64:    self.crate_image_base64_view_element,
            ResultType.HISTOGRAM:       self.crate_histogram_view_element,
            ResultType.MATPLOTLIB_FIG:  self.crate_matplotlib_view_element,
            ResultType.PLOTLY_FIG:      self.crate_plotly_view_element,
        }
        result_title = self.create_result_title()
        result_body = value_type_to_view[self.result_type]()

        self.ref_card_conteiner = Ref[Container]()
        draggable_content = Container(
            ref = self.ref_card_conteiner,
            content = Column([
                result_title,
                result_body
            ]),
            # key = self.node.id,
            data = self,
            border_radius = 10,
            bgcolor = colors.BLACK26,
            padding = padding.only(left=10, top=10, right=10, bottom=10),
        )
        draggable_content_feedback = Container(
            border_radius = 10,
            bgcolor = colors.BLACK26,
            padding = padding.only(left=10, top=10, right=10, bottom=10),
            content = Text(
                (self.current_time if self.current_time else "") + (": " + self.label if self.label else ""),
                color = colors.WHITE54,
                size = 20,
            ),
        )
        return Draggable(
            group = self.group,
            content = draggable_content,
            content_feedback = draggable_content_feedback,
        )
    

    def create_result_title(self):
        """
        Создает заголовок результата
        """
        title = (self.current_time if self.current_time else "") + (": " + self.label if self.label else "")
        return Container(
            content = Row(
                expand = True,
                alignment = MainAxisAlignment.CENTER,
                controls = [Text(
                    value = title,
                    weight = FontWeight.BOLD,
                    size = 20,
                    text_align = TextAlign.CENTER
                )]
            ),
        )
    

    def create_none_view_element(self):
        """
        Создает элемент для отображения None
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Text(value="Нет данных")],
        )
    

    def create_str_view_element(self):
        """
        Создает элемент для отображения строки
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Text(value=self.result_value)],
        )


    def crate_num_view_element(self):
        """
        Создает элемент для отображения числа
        """
        return self.create_str_view_element()
    

    def crate_image_cv2_view_element(self):
        """
        Создает элемент для отображения изображения
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Image(
                src_base64 = self.image_to_base64(self.result_value),
                border_radius = border_radius.all(10),
                fit = ImageFit.FIT_WIDTH,
                expand=True
            )],
        )
    
    
    def crate_image_base64_view_element(self):
        """
        Создает элемент для отображения изображения
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Image(
                src_base64 = self.result_value,
                border_radius = border_radius.all(10),
                fit = ImageFit.FIT_WIDTH,
                expand=True
            )],
        )
    

    def crate_histogram_view_element(self):
        """
        Создает элемент для отображения гистограммы
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [Text(value=self.result_value)],
        )
    

    def crate_matplotlib_view_element(self):
        """
        Создает элемент для отображения графика
        """
        self.result_value = self.fig_to_base64(self.result_value)
        return self.crate_image_base64_view_element()
        # return Row(
        #     alignment = MainAxisAlignment.CENTER,
        #     controls = [MatplotlibChart(
        #         figure = self.result_value,
        #         expand = True,
        #         isolated = True,
        #     )],
        # )
    

    def crate_plotly_view_element(self):
        """
        Создает элемент для отображения графика
        """
        return Row(
            alignment = MainAxisAlignment.CENTER,
            controls = [PlotlyChart(
                figure = self.result_value,
                expand = True,
            )],
        )


    def image_to_base64(self, image):
        # Загрузка изображения
        if image is None:
            return None
        if isinstance(image, str):
            image = cv2.imread(image)
        
        # Кодирование изображения в формате base64
        _, buffer = cv2.imencode('.jpg', image)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        return base64_image
    

    def fig_to_base64(self, fig):
        """
        Преобразует объект fig из matplotlib в изображение в формате base64
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        # return base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    