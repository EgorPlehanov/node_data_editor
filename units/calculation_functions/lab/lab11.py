from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def apply_low_pass_filter(image, cutoff_frequency):
    """
    Применить фильтр Лопаса к входному изображению
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    mask = np.zeros((rows, cols, 2), np.uint8)
    mask[crow - cutoff_frequency:crow + cutoff_frequency, ccol - cutoff_frequency:ccol + cutoff_frequency] = 1

    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    
    return img_back



def apply_high_pass_filter(image, cutoff_frequency: int):
    """
    Применить фильтр Хаффмана к входному изображению
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    mask = np.ones((rows, cols, 2), np.uint8)
    mask[crow - cutoff_frequency:crow + cutoff_frequency, ccol - cutoff_frequency:ccol + cutoff_frequency] = 0

    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    
    return img_back



def fun_apply_low_pass_filter(image, cutoff_frequency: int):
    """
    Применить фильтр Лапласа к входному изображению
    """
    if image is None:
        return {"low_pass_img": None}
    if isinstance(image, File):
        image = read_file(image.path)

    low_pass_img = apply_low_pass_filter(image, cutoff_frequency)
    low_pass_img = np.clip(low_pass_img, 0, 255).astype(np.uint8)

    return {
        "low_pass_img": NodeResult(low_pass_img, ResultType.IMAGE_CV2),
    }



def fun_apply_high_pass_filter(image, cutoff_frequency):
    """
    Применить фильтр Хаффмана к входному изображению
    """
    if image is None:
        return {"high_pass_img": None}
    if isinstance(image, File):
        image = read_file(image.path)

    high_pass_img = apply_high_pass_filter(image, cutoff_frequency)
    # high_pass_img = np.clip(high_pass_img, 0, 255).astype(np.uint8)
    high_pass_img /= np.max(high_pass_img)

    return {
        "high_pass_img": NodeResult(high_pass_img, ResultType.IMAGE_CV2),
    }



def extract_contours(image):
    """
    Функция для выделения контуров объектов на изображении
    """
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 150)
    return edged



def filter_image(image, kernel_type):
    if image is None:
        return {"filtered_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    kernels = {
        'lowpass': np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]) / 9,  # Простой усредняющий фильтр
        'highpass': np.array([
            [-1, -1, -1],
            [-1,  8, -1],
            [-1, -1, -1]
        ]),  # Обнаружение краев
        'gaussian': np.array([
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ]) / 16,  # Гауссовское размытие
        'sharpen': np.array([
            [0, -1,  0],
            [-1,  5, -1],
            [0, -1,  0]
        ]),  # Увеличение резкости
        'edge_detection': np.array([
            [1,  0, -1],
            [0,  0,  0],
            [-1, 0,  1]
        ]),  # Обнаружение краев
        'emboss': np.array([
            [-2, -1,  0],
            [-1,  1,  1],
            [0,  1,  2]
        ]),  # Рельефный фильтр
        'sobel_horizontal': np.array([
            [-1, -2, -1],
            [0,   0,  0],
            [1,   2,  1]
        ]),  # Горизонтальный фильтр Собеля (для обнаружения горизонтальных краев)
        'sobel_vertical': np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ]),
        'box_blur': np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]) / 9,  # Размытие Box Blur
        'laplacian': np.array([
            [0,  1, 0],
            [1, -4, 1],
            [0,  1, 0]
        ]),  # Оператор Лапласиана для обнаружения краев
        'laplacian_diagonal': np.array([
            [1,  1, 1],
            [1, -8, 1],
            [1,  1, 1]
        ]),  # Диагональный Лапласиан для обнаружения краев
        'directional_north': np.array([
            [1,  1, 1],
            [1, -2, 1],
            [-1, -1, -1]
        ]),  # Направленный фильтр (северное направление)
        'directional_east': np.array([
            [-1, 1, 1],
            [-1, -2, 1],
            [-1, 1, 1]
        ]),  # Направленный фильтр (восточное направление)
        'scharr_horizontal': np.array([
            [3, 10, 3],
            [0,  0, 0],
            [-3, -10, -3]
        ]),  # Горизонтальный фильтр Шарра (для обнаружения горизонтальных краев)
        'scharr_vertical': np.array([
            [3,  0,  -3],
            [10, 0, -10],
            [3,  0,  -3]
        ]),
    }

    if kernel_type not in kernels:
        return None
    
    kernel = kernels[kernel_type]
    filtered_image = cv2.filter2D(image, -1, kernel)
    contours = extract_contours(filtered_image)
    # if kernel_type == 'lowpass':
    #     filtered_image = cv2.filter2D(image, -1, kernel)
    # elif kernel_type == 'highpass':
    #     lowpass_filtered = cv2.filter2D(image, -1, kernel)
    #     filtered_image = image - lowpass_filtered
    # else:
    #     raise ValueError("Unsupported filter type. Choose 'lowpass' or 'highpass'.")
    

    return {
        "filtered_image": NodeResult(contours, ResultType.IMAGE_CV2),
    }
