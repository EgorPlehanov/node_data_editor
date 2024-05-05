from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def gradient_sobel(image):
    # Применение операторов Собеля для вычисления градиентов по X и Y
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    # Вычисление магнитуды градиентов
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    gradient_magnitude = np.uint8(np.absolute(gradient_magnitude))
    
    return gradient_magnitude



def laplacian_operator(image):
    # Применение оператора Лапласа
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    laplacian = np.uint8(np.absolute(laplacian))
    
    return laplacian



def thresholding(image, threshold_value=40):
    # Пороговое преобразование для выделения контуров
    _, thresholded_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
    return thresholded_image



def sharpen_image(image):
    # Повышение четкости изображения с использованием Лапласиана
    laplacian = laplacian_operator(image)
    sharpened = cv2.addWeighted(image, 1.5, laplacian, -0.5, 0)
    return sharpened



def apply_gradient_and_laplacian(image, method='gradient'):
    """
    Выделения контуров объектов на изображении методом морфологических преобразований
    """
    if image is None:
        return {"thresholding_image": None}
    if isinstance(image, File):
        # image = read_file(image.path)
        image = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)

    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if method == 'gradient':
        contours_img = gradient_sobel(image)
    elif method == 'laplacian':
        contours_img = laplacian_operator(image)
    else:
        return {"thresholding_image": NodeResult("Некорректный метод", ResultType.STR_VALUE)}
    

    # Пороговое преобразование
    thresholding_image = thresholding(contours_img)
    
    return {
        "thresholding_image": NodeResult(thresholding_image, ResultType.IMAGE_CV2),
    }