from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def add_random_noise(image, mean=0, stddev=10):
    """
    Функция для добавления случайного шума с нормальным распределением

    mean: среднее значение случайного шума
    stddev: стандартное отклонение случайного шума
    """
    if image is None:
        return {"noisy_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    noise = np.random.normal(mean, stddev, image.shape).astype(np.uint8)
    noisy_image = cv2.add(image, noise)

    return {
        "noisy_image": NodeResult(noisy_image, ResultType.IMAGE_CV2),
        "noise": NodeResult(noise, ResultType.IMAGE_CV2)
    }



def add_impulse_noise(image, salt_vs_pepper_ratio=0.05):
    """
    Функция для добавления импульсного шума (соль-и-перец)

    salt_vs_pepper_ratio: доля белых пятен в изображении
    """
    if image is None:
        return {"noisy_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    
    noisy_image = np.copy(image)
    salt_vs_pepper = salt_vs_pepper_ratio / 2
    
    # Генерация координат для соли (белые пятна)
    num_salt = np.ceil(salt_vs_pepper * image.size)
    salt_coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    noisy_image[salt_coords[0], salt_coords[1]] = 255
    
    # Генерация координат для перца (черные пятна)
    num_pepper = np.ceil(salt_vs_pepper * image.size)
    pepper_coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    noisy_image[pepper_coords[0], pepper_coords[1]] = 0
    
    # Создание изображения шума (маска шума)
    noise_image = np.zeros(image.shape, dtype=np.uint8)
    noise_image[salt_coords[0], salt_coords[1]] = 255  # белые пятна
    noise_image[pepper_coords[0], pepper_coords[1]] = 0  # черные пятна
    
    return {
        "noisy_image": NodeResult(noisy_image, ResultType.IMAGE_CV2),
        "noise": NodeResult(noise_image, ResultType.IMAGE_CV2)
    }



def add_mixed_noise(image, mean=0, stddev=10, salt_vs_pepper_ratio=0.05):
    """
    Функция для добавления смеси двух типов шумов
    """
    if image is None:
        return {"noisy_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    random_noise_result = add_random_noise(image, mean, stddev)
    noisy_image = random_noise_result["noisy_image"].value
    random_noise = random_noise_result["noise"].value

    impulse_noise_result = add_impulse_noise(noisy_image, salt_vs_pepper_ratio)
    noisy_image = impulse_noise_result["noisy_image"].value
    impulse_noise = impulse_noise_result["noise"].value

    return {
        "noisy_image": NodeResult(noisy_image, ResultType.IMAGE_CV2),
        "random_noise": NodeResult(random_noise, ResultType.IMAGE_CV2),
        "impulse_noise": NodeResult(impulse_noise, ResultType.IMAGE_CV2)
    }



def apply_average_filter(image, kernel_size_x=3, kernel_size_y=3):
    """
    Функция для применения усредняющего арифметического фильтра

    kernel_size_x: ширина ядра
    kernel_size_y: высота ядра
    """
    if image is None:
        return {"anti_noisy_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    blurred_image = cv2.blur(image, (kernel_size_x, kernel_size_y))

    return {
        "anti_noisy_image": NodeResult(blurred_image, ResultType.IMAGE_CV2)
    }



def apply_median_filter(image, kernel_size=3):
    """
    Функция для применения медианного фильтра

    kernel_size: размер ядра
    """
    if image is None:
        return {"anti_noisy_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    filtered_image = cv2.medianBlur(image, kernel_size)

    return {
        "anti_noisy_image": NodeResult(filtered_image, ResultType.IMAGE_CV2)
    }