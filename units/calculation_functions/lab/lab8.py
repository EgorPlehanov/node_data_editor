from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import numpy as np
import cv2



def fourier2D(image: np.ndarray) -> np.ndarray:
    # Применяем преобразование Фурье для каждой строки изображения
    fourier_rows = np.fft.fft(image, axis=0)

    # Затем применяем преобразование Фурье для каждого столбца полученной матрицы
    fourier_2D = np.fft.fft(fourier_rows, axis=1)

    return fourier_2D


def inverse_fourier2D(complex_spectrum: np.ndarray) -> np.ndarray:
    # Выполняем обратное преобразование Фурье для каждого столбца полученной матрицы
    inverse_fourier_rows = np.fft.ifft(complex_spectrum, axis=0)

    # Затем выполняем обратное преобразование Фурье для каждой строки
    inverse_fourier_2D = np.fft.ifft(inverse_fourier_rows, axis=1)

    return inverse_fourier_2D



def fun_fourier2D(image) -> np.ndarray:
    if image is None:
        return {"furier_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    fourier_transformed_image = fourier2D(image)

    # Получаем амплитудный спектр (модуль 2-D спектра)
    amplitude_spectrum = np.abs(fourier_transformed_image)

    # Сдвигаем нулевую частоту в центр спектра
    shifted_spectrum = np.fft.fftshift(amplitude_spectrum)
    
    # Нормализуем амплитудный спектр к диапазону [0.0, 1.0]
    min_val = np.min(shifted_spectrum)
    max_val = np.max(shifted_spectrum)
    normalized_spectrum = (shifted_spectrum - min_val) / (max_val - min_val)

    return {
        "furier_image": NodeResult(normalized_spectrum, ResultType.IMAGE_CV2),
        "furier_image_value": NodeResult(fourier_transformed_image, ResultType.IMAGE_CV2),
    }



def fun_inverse_fourier2D(image) -> np.ndarray:
    if image is None:
        return {"inverse_furier_image": None}
    # if isinstance(image, File):
    #     image = read_file(image.path)

    inverse_furier_image = inverse_fourier2D(image)
    inverse_furier_image = np.uint8(np.clip(inverse_furier_image, 0, 255))

    return {
        "inverse_furier_image": NodeResult(inverse_furier_image, ResultType.IMAGE_CV2),
    }