from enum import Enum
from dataclasses import dataclass
from typing import Any



class ResultType(Enum):
    '''Тип результата выполнения узла'''
    NONE = "none"
    STR_VALUE = "str"
    NUMBER_VALUE = "num"
    IMAGE_CV2 = "img_cv2"
    IMAGE_BASE64 = "img_base64"
    HISTOGRAM = "hist"
    MATPLOTLIB_FIG = "matplotlib_fig"
    PLOTLY_FIG = "plotly_fig"

    def __str__(self):
        return self.value
    


@dataclass
class NodeResult:
    '''Результат выполнения узла'''
    value: Any = None
    type: ResultType = ResultType.NONE