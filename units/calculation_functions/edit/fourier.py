from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np
import matplotlib.pyplot as plt



def fourier_2d_to_show(image_path, is_gamma_transform=False):
    """
    Применить прямое 2-D преобразование Фурье
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    img_fft2D = np.fft.ifftshift(image)
    img_fft2D = np.fft.fft2(img_fft2D)
    img_fft2D = np.fft.fftshift(img_fft2D)

    def gamma_transform(img, C, gamma):
        if img.ndim == 1:
            img = np.reshape(img, (1024, 1024))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                img[i][j] = C * pow(img[i][j], gamma)
        return img
    # Повышение яркости для улучшения качества картинки
    if is_gamma_transform:
        img_fft2D = gamma_transform(img_fft2D, 1, 0.1)

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.imshow(abs(img_fft2D), cmap='gray')
    return fig



def fourier_2d(image, is_gamma_transform: bool = False):
    """
    Применить прямое 2-D преобразование Фурье
    """
    if image is None:
        return {"fourier_image": None, "fourier_image_show": None}
    if isinstance(image, File):
        fig_fft = fourier_2d_to_show(image.path, is_gamma_transform)
        image = read_file(image.path)

    f_transform = np.fft.fft2(image)
    fourier_image = np.fft.fftshift(f_transform)


    return {
        "fourier_image": NodeResult(fourier_image, ResultType.IMAGE_CV2),
        "fourier_image_show": NodeResult(fig_fft, ResultType.MATPLOTLIB_FIG),
    }


    
def inverse_fourier_2d(image):
    """
    Обратное 2-D преобразование Фурье
    """
    if image is None:
        return {"inverse_fourier_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    # Обратное 2-D преобразование Фурье
    f_inverse = np.fft.ifft2(np.fft.ifftshift(image))
    # Получаем действительную часть изображения
    reconstructed_image = np.real(f_inverse)
    # Масштабируем значения пикселей в диапазон 0-255
    reconstructed_image = cv2.normalize(reconstructed_image, None, 0, 255, cv2.NORM_MINMAX)
    # Преобразуем в формат uint8 (8-битное целое без знака)
    reconstructed_image = np.uint8(reconstructed_image)

    return {
        "inverse_fourier_image": NodeResult(reconstructed_image, ResultType.IMAGE_CV2),
    }