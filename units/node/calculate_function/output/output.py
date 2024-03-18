from flet import *
from typing import Any
from datetime import datetime
from ..calculate_function_typing import *



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
    