from enum import Enum
from dataclasses import dataclass
from typing import Any



class ResultType(Enum):
    '''
    Тип результата выполнения узла
    
    NONE - ничего не возвращает
    STR_VALUE - строковое значение
    NUMBER_VALUE - числовое значение
    IMAGE_CV2 - изображение в формате OpenCV
    IMAGE_BASE64 - изображение в формате base64
    HISTOGRAM - гистограмма matplotlib.
    '''

    NONE = "none"
    STR_VALUE = "str"
    NUMBER_VALUE = "num"
    IMAGE_CV2 = "img_cv2"
    IMAGE_BASE64 = "img_base64"
    HISTOGRAM = "hist"
    MATPLOTLIB_FIG = "matplotlib_fig"
    PLOTLY_FIG = "plotly_fig"


    def __str__(self) -> str:
        return self.value
    


@dataclass
class NodeResult:
    '''
    Результат выполнения узла

    value - значение результата
    type - тип результата
    '''

    value: Any = None
    type: ResultType = ResultType.NONE
    