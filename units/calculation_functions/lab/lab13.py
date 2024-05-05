from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def erosion(image, kernel_size):
    """
    Выделения контуров объектов на изображении методом ЭРОЗИИ
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded_image = cv2.erode(image, kernel, iterations=1)
    return eroded_image



def dilation(image, kernel_size):
    """
    Выделения контуров объектов на изображении методом ДИЛЯЦИИ
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated_image = cv2.dilate(image, kernel, iterations=1)
    return dilated_image



def contours_from_morphology(image, method='erosion', kernel_size=3):
    """
    Выделения контуров объектов на изображении методом морфологических преобразований
    """
    if image is None:
        return {"morphology_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    if method == 'erosion':
        morph_image = erosion(image, kernel_size)
    elif method == 'dilation':
        morph_image = dilation(image, kernel_size)
    else:
        return {"morphology_image": NodeResult("Некорректный метод", ResultType.STR_VALUE)}
    
    # Вычисление разницы между исходным и морфологически обработанным изображением
    contour_image = cv2.absdiff(image, morph_image)
    
    # Пороговое преобразование для выделения контуров
    _, thresholded_image = cv2.threshold(contour_image, 40, 255, cv2.THRESH_BINARY)
    
    return {
        "morphology_image": NodeResult(thresholded_image, ResultType.IMAGE_CV2),
    }