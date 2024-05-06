from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import numpy as np
import cv2
import math


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



def lpf_reverse(lpw):
    return lpw[:0:-1] + lpw


def lpf(fc, m, dt):
        d = [0.35577019, 0.2436983, 0.07211497, 0.00630165]
        fact = fc * dt
        lpw = []
        lpw.append(fact)
        arg = fact * math.pi
        for i in range(1, m + 1):
            lpw.append(np.sin(arg * i) / (math.pi * i))
        lpw[m] = lpw[m] / 2
        sumg = lpw[0]
        for i in range(1, m + 1):
            sum = d[0]
            arg = math.pi * i / m
            for k in range(1, 4):
                sum += 2 * d[k] * np.cos(arg * k)
            lpw[i] = lpw[i] * sum
            sumg += 2 * lpw[i]
        for i in range(m + 1):
            lpw[i] = lpw[i] / sumg
        return lpw


def convolModel(x, h, N, M):
        out_data = []
        for i in range(N):
            y = 0
            for j in range(M):
                y += x[i-j] * h[j]
            out_data.append(y)
        return out_data


def fourier_resize_image2_main(image, scale_factor_height, scale_factor_width, mode):
    # Пусть к исходному изображению
    global img_ifft2D_1, img_ifft2D


    # Чтение исходного изображения
    img_source = image
    
    # Определение разрешения изображения
    height = img_source.shape[0]
    width = img_source.shape[1]

    # Коэффициент изменения разрешения
    N = scale_factor_height
    M = scale_factor_width

    # Разрешение итоговое
    height_1 = int(height * N)
    width_1 = int(width * M)

    height_2 = int(height / N)
    width_2 = int(width / M)

    # Прямое 2D преобразование Фурье
    img_fft2D = np.fft.ifftshift(img_source)
    img_fft2D = np.fft.fft2(img_fft2D)
    img_fft2D = np.fft.fftshift(img_fft2D)

    # Увеличение изображения
    if mode == "increase":
        # Start/Stop
        height_start = int((height_1 - height) / 2)
        width_start = int((width_1 - width) / 2)

        img_ifft2D = np.zeros((height_1, width_1), dtype=complex)
        # img_ifft2D[:, (height - width) / 2:(height + width) / 2] = img_fft2D
        for i in range(height_start, height + height_start):
            for j in range(width_start, width + width_start):
                img_ifft2D[i][j] = img_fft2D[i - height_start][j - width_start]

    # Уменьшение изображения
    elif mode == "decrease":
        # Start/Stop
        height_start = int((height - height_2) / 2)
        width_start = int((width - width_2) / 2)

        img_ifft2D_1 = img_fft2D.copy()
        fc = 0.5 / N
        m = 1
        M_1 = 2 * m + 1
        N_1 = width  # 480
        N_2 = height  # 360
        dt = 1

        # ФНЧ
        low_pass_filter = lpf_reverse(lpf(fc, m, dt))

        # Построчная свертка с ФНЧ
        for i in range(0, height):
            img_ifft2D_1[i] = convolModel(img_ifft2D_1[i], low_pass_filter, N_1, M_1)
            img_ifft2D_1[i] = np.roll(img_ifft2D_1[i], -m)

        img_ifft2D_1 = np.rot90(img_ifft2D_1)
        for i in range(0, width):
            img_ifft2D_1[i] = convolModel(img_ifft2D_1[i], low_pass_filter, N_2, M_1)
            img_ifft2D_1[i] = np.roll(img_ifft2D_1[i], -m)

        img_ifft2D_1 = np.rot90(img_ifft2D_1, -1)
        img_ifft2D = np.zeros((height_2, width_2), dtype=complex)
        for i in range(0, height_2):
            for j in range(0, width_2):
                img_ifft2D[i][j] = img_ifft2D_1[i + height_start][j + width_start]

    # Обратное 2D преобразование Фурье
    img_ifft2D = np.fft.ifftshift(img_ifft2D)
    img_ifft2D = np.fft.ifft2(img_ifft2D)
    img_ifft2D = np.fft.fftshift(img_ifft2D)

    return img_source, abs(img_fft2D), abs(img_ifft2D)



def fourier_resize_image2(image, scale_factor_height, scale_factor_width, mode):
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    
    img_source, img_fft2D, img_ifft2D = fourier_resize_image2_main(
        image,
        scale_factor_height, scale_factor_width,
        mode
    )
    
    # img_ifft2D

    return {
        "resized_image_spectrum": NodeResult(img_fft2D, ResultType.IMAGE_CV2),
        "resized_image": NodeResult(img_ifft2D, ResultType.IMAGE_CV2),
    }