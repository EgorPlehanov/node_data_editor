from ..calculate_function_typing import *

from typing import Any
from datetime import datetime



def display_result(result: Any, label: str):
    """
    Функция вывода значения
    """
    cur_time = datetime.now().strftime("%H:%M:%S")
    return {"result": {
        "result": result,
        "label": label,
        "current_time": cur_time
    }}
    