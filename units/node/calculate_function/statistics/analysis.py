import cv2
import numpy as np
from ....parameters.parameter_typing import File
from ..input.read import read_file
from ..calculate_function_typing import *



def compute_difference_image(image1, image2):
    """
    Вычисляет разностное изображение между двумя входными изображениями.
    """
    if image1 is None or image2 is None:
        return {"difference_image": None}
    if isinstance(image1, File):
        image1 = read_file(image1.path)
    if isinstance(image2, File):
        image2 = read_file(image2.path)

    desired_width, desired_height = get_desired_dimensions(image1, image2)

    # Приводим изображения к одному размеру
    image1_resized = resize_image(image1, desired_width, desired_height)
    image2_resized = resize_image(image2, desired_width, desired_height)

    difference_image = cv2.absdiff(image1_resized, image2_resized)
    return {
        "difference_image": NodeResult(difference_image, ResultType.IMAGE_CV2),
    }


def get_desired_dimensions(image1, image2):
    """
    Определяет желаемую ширину и высоту для приведения изображений к одному размеру.
    """
    height1, width1 = image1.shape[:2]
    height2, width2 = image2.shape[:2]

    desired_height = max(height1, height2)
    desired_width = max(width1, width2)

    return desired_width, desired_height


def resize_image(image, desired_width, desired_height):
    """
    Приводит входное изображение к заданным размерам.
    """
    return cv2.resize(image, (desired_width, desired_height))


def apply_optimal_histogram_equalization(image):
    """
    Применяет оптимальное градационное преобразование к разностному изображению
    """
    if image is None:
        return {"optimal_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    # optimal_image = cv2.equalizeHist(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    optimal_image = cv2.equalizeHist(gray_image) 
    return {
        "optimal_image": NodeResult(optimal_image, ResultType.IMAGE_CV2),
    }