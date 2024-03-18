from ....parameters.parameter_typing import File
from ..calculate_function_typing import *
from ..input.read import read_file
import cv2
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np



def plot_image_histogram(image):
    """
    Строит гистограмму распределения цветов изображения по каналам или яркости,
    в зависимости от типа изображения.
    """
    if image is None:
        return {"histogram_dataframe": None}
    if isinstance(image, File):
        image = read_file(image.path)

    fig, ax = plt.subplots()
    if len(image.shape) == 3:  # Check for color image
        if image.dtype == 'uint8':  # Check for image format
            color = ('b', 'g', 'r')
            for k, col in enumerate(color):
                hist_values = cv2.calcHist([image], [k], None, [256], [0, 256])
                ax.plot(hist_values, color=col, label=col)
    else:  # Grayscale image
        if image.dtype == 'uint8':  # Check for image format
            hist_values = cv2.calcHist([image], [0], None, [256], [0, 256])
            ax.plot(hist_values, label='grayscale')

    ax.set_xlim([0, 256])
    ax.legend()

    return {
        "histogram_fig": NodeResult(fig, ResultType.MATPLOTLIB_FIG),
    }



def plot_brightness_histogram(image):
    """
    Построение гистограммы яркости изображения
    """
    if image is None:
        return {"histogram_dataframe": None}
    if isinstance(image, File):
        image = read_file(image.path)

    # Преобразование изображения в оттенки серого, если оно не является таковым
    if len(image.shape) == 3:
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = image

    # Построение гистограммы
    fig = plt.figure()
    plt.hist(gray_img.flatten(), bins=256, range=[0, 256], color='gray')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.title('Гистограмма яркости изображения')
    
    return {
        "histogram_fig": NodeResult(fig, ResultType.MATPLOTLIB_FIG),
    }