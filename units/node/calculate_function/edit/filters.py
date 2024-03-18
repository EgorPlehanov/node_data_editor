from ....parameters.parameter_typing import File
from ..input.read import read_file
from ..calculate_function_typing import *
import cv2
import numpy as np
from matplotlib import pyplot as plt
from ..statistics.histogram import plot_brightness_histogram



def apply_grayscale_scaling(image, scale_size: int = 255):
    """
    Применяет шкалирование серого цвета к входному изображению и возвращает результат
    """
    if image is None:
        return {"grayscale_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    min_val, max_val = np.min(image), np.max(image)
    scaled_image = ((image - min_val) / (max_val - min_val)) * scale_size
    return {
        "grayscale_image": NodeResult(scaled_image.astype(np.uint8), ResultType.IMAGE_CV2)
    }



def negative_transformation(image):
    """
    Применяет негативное градационное преобразование к изображению.
    """
    if image is None:
        return {"negative_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    L = np.iinfo(image.dtype).max
    negative_image = L - 1 - image
    return {
        "negative_image": NodeResult(negative_image, ResultType.IMAGE_CV2)
    }



def gamma_correction(image, gamma: float = 1.0, constant: float = 1.0):
    """
    Применяет гамма-преобразование к изображению.
    """
    if image is None:
        return {"gamma_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    gamma_image = constant * np.power(image, gamma)
    gamma_image = np.clip(gamma_image, 0, 255).astype(np.uint8)
    return {
        "gamma_image": NodeResult(gamma_image, ResultType.IMAGE_CV2)
    }



def logarithmic_transformation(image, constant=1):
    """
    Применяет логарифмическое градационное преобразование к изображению.
    """
    if image is None:
        return {"logarithmic_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    logarithmic_image = np.uint8(constant * np.log1p(image + 1))
    return {
        "logarithmic_image": NodeResult(logarithmic_image, ResultType.IMAGE_CV2)
    }



def image_histogram_equalization(image):
    """
    Градационное преобразование изображения путем эквализации его гистограммы
    """
    if image is None:
        return {"equalization_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    # a) Рассчитать нормализованную гистограмму
    hist, _ = np.histogram(image.flatten(), bins=256, range=[0, 256])
    hist_norm = hist / (image.shape[0] * image.shape[1])

    # b) Вычислить функцию распределения
    cdf = hist_norm.cumsum()

    # c) Использовать CDF для пересчета яркостей
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    cdf_normalized = cdf_normalized.astype('uint8')

    # Применить функцию распределения
    img_equalized = cdf_normalized[image]

    # # Построить гистограмму оригинального изображения
    # fig_orig = plt.figure()
    # plt.hist(image.flatten(), bins=256, range=[0,256], color='r')
    # plt.xlabel('Интенсивность')
    # plt.ylabel('Частота')
    # plt.title('Оригинальная гистограмма')

    # # Построить гистограмму преобразованного изображения
    # fig_equalized = plt.figure()
    # plt.hist(img_equalized.flatten(), bins=256, range=[0,256], color='b')
    # plt.xlabel('Интенсивность')
    # plt.ylabel('Частота')
    # plt.title('Гистограмма после эквализации')

    fig_orig = plot_brightness_histogram(image)["histogram_fig"]
    fig_equalized = plot_brightness_histogram(img_equalized)["histogram_fig"]

    return {
        "equalization_image": NodeResult(img_equalized, ResultType.IMAGE_CV2),
        'original_hist': fig_orig,
        'equalized_hist': fig_equalized,
    }