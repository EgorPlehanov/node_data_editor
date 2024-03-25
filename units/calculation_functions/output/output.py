from ..calculation_functions_typing import *

from typing import Any
from datetime import datetime



def display_result(result: Any, label: Any) -> dict:
    """
    Функция вывода значения
    """
    cur_time = datetime.now().strftime("%H:%M:%S")
    return {"result": {
        "result": result,
        "label": str(label),
        "current_time": cur_time
    }}
    