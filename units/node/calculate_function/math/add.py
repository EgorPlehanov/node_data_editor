from ..calculate_function_typing import *



def add_two_numbers(a: float, b: float) -> float:
    """
    Сложение двух чисел
    """
    sum_value = a + b
    return {
        "sum": NodeResult(sum_value, ResultType.NUMBER_VALUE)
    }