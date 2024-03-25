from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file
from .filters import apply_grayscale_scaling

import cv2
import numpy as np
import matplotlib.pyplot as plt



def calculate_derivative(image):
    """
    Рассчитываем производные строки изображения
    """
    derivative = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    # derivative = np.abs(np.gradient(image.astype(float), axis=0))
    return derivative


def calculate_autocorrelation(derivative):
    """
    Рассчитываем автокорреляционную функцию (АКФ) производных строк изображения
    """
    autocorr = np.correlate(derivative.flatten(), derivative.flatten(), mode='same')
    # autocorr = np.correlate(derivative, derivative, mode='same')
    return autocorr


def calculate_crosscorrelation(derivative1, derivative2):
    """
    Рассчитываем взаимную корреляционную функцию (ВКФ) производных двух строк изображения
    """
    # crosscorr = np.correlate(derivative1, derivative2, mode='same')
    crosscorr = np.correlate(derivative1.flatten(), derivative2.flatten(), mode='same')
    return crosscorr


def plot_spectrum(signal, title):
    """
    Рассчитываем и отображаем спектр сигнала
    """
    spectrum = np.fft.fftshift(np.abs(np.fft.fft(signal)))
    freq = np.fft.fftshift(np.fft.fftfreq(len(signal)))
    
    fig, ax = plt.subplots()
    ax.plot(freq, spectrum)
    ax.set_title(title)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Magnitude')
    ax.grid(True)
    
    return fig


def detect_artifacts(image, is_grayscale: bool):
    """
    Функция для обнаружения артефактов в рентгеновском изображении
    """
    if image is None:
        return {
            "original_spectrum": None,
            "derivative_spectrum": None,
            "autocorrelation": None,
            "crosscorrelation": None
        }
    if isinstance(image, File):
        image = read_file(image.path)

    if is_grayscale:
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = apply_grayscale_scaling(image)["grayscale_image"].value

    # Рассчитываем производные строки изображения
    derivative = calculate_derivative(image)
    
    # Рассчитываем АКФ производных строк изображения
    autocorr = calculate_autocorrelation(derivative)
    
    # Рассчитываем ВКФ производных строк изображения
    crosscorr = calculate_crosscorrelation(derivative[:-1], derivative[1:])
    
    # Отображаем спектры
    original_spectrum_fig = plot_spectrum(
        image.mean(axis=1), 'Original Image Spectrum'
    )
    derivative_spectrum_fig = plot_spectrum(
        derivative.mean(axis=1), 'Derivative Image Spectrum'
    )
    autocorrelation_fig = plot_spectrum(
        autocorr, 'Autocorrelation of Derivative Image'
    )
    crosscorrelation_fig = plot_spectrum(
        crosscorr, 'Crosscorrelation of Derivative Image'
    )
    
    return {
        "original_spectrum": NodeResult(
            original_spectrum_fig, ResultType.MATPLOTLIB_FIG
        ),
        "derivative_spectrum": NodeResult(
            derivative_spectrum_fig, ResultType.MATPLOTLIB_FIG
        ),
        "autocorrelation": NodeResult(
            autocorrelation_fig, ResultType.MATPLOTLIB_FIG
        ),
        "crosscorrelation": NodeResult(
            crosscorrelation_fig, ResultType.MATPLOTLIB_FIG
        ),
    }
