from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import numpy as np



# Функция для прямого 2-D преобразования Фурье
def Fourier2D(image):
    return np.fft.fft2(image)


# Функция для обратного 2-D преобразования Фурье
def inverseFourier2D(image):
    return np.fft.ifft2(image)


# Увеличение размера изображения в 1.n раз
def resize_image(image, scale_factor):
    # Применяем прямое 2-D преобразование Фурье
    fourier_image = Fourier2D(image)
    
    # Получаем размеры изображения
    M, N = image.shape[:2]
    
    # Рассчитываем новый размер
    new_M = int(M * scale_factor)
    new_N = int(N * scale_factor)
    
    # Увеличиваем изображение, дополняя нулями
    new_image = np.zeros((new_M, new_N), dtype=np.complex128)
    new_image[:M//2, :N//2] = fourier_image[:M//2, :N//2]
    new_image[new_M-M//2:, :N//2] = fourier_image[M//2:, :N//2]
    new_image[:M//2, new_N-N//2:] = fourier_image[:M//2, N//2:]
    new_image[new_M-M//2:, new_N-N//2:] = fourier_image[M//2:, N//2:]
    
    # Применяем обратное 2-D преобразование Фурье
    resized_image = inverseFourier2D(new_image)
    
    # Возвращаем вещественную часть результата
    return np.abs(resized_image)



def fourier_resize_image(image, scale_factor):
    """
    Меняет размер изображения с использованием прямого 2-D преобразования Фурье
    """
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    
    resized_image = resize_image(image, scale_factor).astype(np.uint8)

    return {
        "resized_image": NodeResult(resized_image, ResultType.IMAGE_CV2),
    }