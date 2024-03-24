from ..calculate_function_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def shift_image_by_constant(image, shift_constant: float = 30):
    """
    LAB_NAME: shift_2D
    Сдвигает входное изображение путем добавления константного значения к каждому пикселю
    """
    if image is None:
        return {"shifted_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    shifted_image = np.clip(image + shift_constant, 0, 255).astype(np.uint8)
    return {
        "shifted_image": NodeResult(shifted_image, ResultType.IMAGE_CV2),
    }


def multiply_image_by_constant(image, multiply_constant: float = 1.3):
    """
    LAB_NAME: multModel_2D
    Умножает каждый пиксель входного изображения на константное значение
    """
    if image is None:
        return {"multiply_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    modified_image = np.clip(image * multiply_constant, 0, 255).astype(np.uint8)
    return {
        "multiply_image": NodeResult(modified_image, ResultType.IMAGE_CV2),
    }


def shift_image(image, dx: int, dy: int):
    """
    Сдвигает входное изображение на указанные значения dx (горизонтальный сдвиг) и dy (вертикальный сдвиг)
    """
    if isinstance(image, File):
        image = read_file(image.path)
    rows, cols = image.shape[:2]
    translation_matrix = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted_image = cv2.warpAffine(image, translation_matrix, (cols, rows))
    return {
        "shifted_image": NodeResult(shifted_image, ResultType.IMAGE_CV2),
    }
