from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import numpy as np



def read_image_from_dat(file_path: str, width: int, height: int) -> np.ndarray:
    """
    Функция для чтения изображения из файла формата .dat.

    Args:
        file_path (str): Путь к файлу .dat.
        width (int): Ширина изображения.
        height (int): Высота изображения.

    Returns:
        image (np.ndarray): Считанное изображение в виде массива numpy.
    """
    try:
        # Считываем данные из файла .dat как одномерный массив float32
        image_data = np.fromfile(file_path, dtype=np.float32)
        # Проверяем, что количество считанных данных соответствует размерам изображения
        assert len(image_data) == width * height, "Неверные размеры изображения"
        # Преобразуем одномерный массив в двумерный массив, представляющий изображение
        image = np.reshape(image_data, (height, width))

        return image
    except Exception as e:
        print(f"Ошибка при чтении изображения: {e}")
        return None

def inverse_filter_without_noise(
    image: np.ndarray, kernel: np.ndarray
) -> np.ndarray:
    """
    Функция для выполнения построчной обратной фильтрации смазанных изображений без шума.

    Args:
        image (np.ndarray): Искаженное изображение.
        kernel (np.ndarray): Ядро функции искажения.

    Returns:
        np.ndarray: Восстановленное изображение.
    """
    # Расширяем размерность ядра функции искажения до соответствующих размеров изображения
    kernel_padded = np.pad(
        kernel, ((0, 0), (0, image.shape[1] - kernel.shape[1])), mode="constant"
    )

    # Вычисляем комплексный спектр строки искаженного изображения
    G = np.fft.fft(image, axis=1)

    # Вычисляем комплексный спектр функции искажения
    H = np.fft.fft(kernel_padded, axis=1)

    # Выполняем построчную обратную фильтрацию для устранения искажений без шума
    X_hat = G / H

    # Выполняем обратное преобразование Фурье для получения восстановленного изображения
    restored_image = np.fft.ifft(X_hat, axis=1).real

    # Нормализуем значения восстановленного изображения к диапазону [0, 1]
    restored_image = (restored_image - np.min(restored_image)) / (
        np.max(restored_image) - np.min(restored_image)
    )

    return restored_image


def inverse_filter_with_noise(
    image: np.ndarray, kernel: np.ndarray, alpha: float
) -> np.ndarray:
    """
    Функция для выполнения построчной обратной фильтрации зашумленных изображений с применением регуляризации.

    Args:
        image (np.ndarray): Искаженное и зашумленное изображение.
        kernel (np.ndarray): Ядро функции искажения.
        alpha (float): Параметр регуляризации.

    Returns:
        np.ndarray: Восстановленное изображение.
    """
    # Расширяем размерность ядра функции искажения до соответствующих размеров изображения
    kernel_padded = np.pad(
        kernel, ((0, 0), (0, image.shape[1] - kernel.shape[1])), mode="constant"
    )

    # Вычисляем комплексный спектр строки искаженного и зашумленного изображения
    G = np.fft.fft(image, axis=1)

    # Вычисляем комплексный спектр функции искажения
    H = np.fft.fft(kernel_padded, axis=1)

    # Выполняем построчную обратную фильтрацию для устранения искажений и шума
    X_hat = G * np.conj(H) / (np.abs(H) ** 2 + alpha**2)

    # Выполняем обратное преобразование Фурье для получения восстановленного изображения
    restored_image = np.fft.ifft(X_hat, axis=1).real

    # Нормализуем значения восстановленного изображения к диапазону [0, 1]
    restored_image = (restored_image - np.min(restored_image)) / (
        np.max(restored_image) - np.min(restored_image)
    )

    return restored_image



def restore_blurred_image(
    image, height_img, width_img,
    kernel_image, height_kernel, width_kernel,
    alpha = 0
):
    
    if image is None or kernel_image is None:
        return {"restored_image": None}
    
    if isinstance(image, File):
        image = read_image_from_dat(image.path, width_img, height_img)   
    if isinstance(kernel_image, File):
        kernel = read_image_from_dat(kernel_image.path, width_kernel, height_kernel)
    
    if alpha == 0:
        restored_image = inverse_filter_without_noise(image, kernel)
    else:
        restored_image = inverse_filter_with_noise(image, kernel, alpha)

    return {
        "restored_image": NodeResult(restored_image, ResultType.IMAGE_CV2)
    }