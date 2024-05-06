from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def rotate_image_90_degrees(image, angle: int):
    """
    Поворачивает растровое изображение на угол, кратный 90 градусам.
    """
    num_rotations = int(angle) // 90
    return np.rot90(image, k=num_rotations)


def fourier(data: np.ndarray) -> pd.DataFrame:
    fourier_transform = np.fft.fft(data)
    amplitude_spectrum = np.abs(fourier_transform)

    return pd.DataFrame(
        {
            "Re[Xn]": fourier_transform.real,
            "Im[Xn]": fourier_transform.imag,
            "|Xn|": amplitude_spectrum,
        }
    )


def spectr_fourier(data: np.ndarray, dt: float) -> pd.DataFrame:
    n = len(data) // 2
    fourier_data = fourier(data)
    xn_values = fourier_data["|Xn|"].values
    f_border = 1 / (2 * dt)
    delta_f = f_border / n
    frequencies = np.arange(n) * delta_f

    return pd.DataFrame({"f": frequencies, "|Xn|": xn_values[:n]})



def spectr_fourier_plot(image, selected_line, dt):

    line_spectr = spectr_fourier(data=image[selected_line], dt=dt)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the Fourier spectrum
    ax.plot(line_spectr['f'], line_spectr['|Xn|'], color='blue')
    ax.set_title('Спектр Фурье для исходной линии')
    ax.set_xlabel('Частота')
    ax.set_ylabel('Амплитуда')
    
    # Return the figure object
    return fig




def compute_derivative(line_from_image: np.ndarray) -> np.ndarray:
    """
    Вычисляет производную из линии изображения.

    Аргументы:
    image (np.ndarray): Исходное изображение в виде массива значений пикселей.

    Возвращает:
    np.ndarray: Массив производной линии изображения.
    """

    # Вычисляем производную выбранной линии
    derivative_line = np.gradient(line_from_image)

    return derivative_line


def compute_derivative_plot(image, selected_line):
    derivative_line = compute_derivative(image[selected_line])
    line_spectr = spectr_fourier(data=derivative_line, dt=1)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the Fourier spectrum
    ax.plot(line_spectr['f'], line_spectr['|Xn|'], color='blue')
    ax.set_title('Спектр Фурье для производной исходной линии')
    ax.set_xlabel('Частота')
    ax.set_ylabel('Амплитуда')
    
    # Return the figure object
    return fig, derivative_line



def acf(data: np.ndarray) -> pd.DataFrame:
    """
    Вычисляет автокорреляционную функцию (ACF) для входного массива данных.

    Параметры:
        data (np.ndarray): Входной массив данных, для которого необходимо рассчитать ACF или CCF.
        function_type (str): Тип функции для расчета, либо "Автокорреляционная функция" для ACF, либо "Ковариационная функция" для CCF.

    Возвращает:
        pd.DataFrame: DataFrame, содержащий значения лагов 'L' и соответствующие значения ACF или CCF 'AC'.
    """
    data_mean = np.mean(data)
    n = len(data)
    l_values = np.arange(0, n)
    ac_values = []

    for L in l_values:
        numerator = np.sum(
            (data[: n - L - 1] - data_mean) * (data[L : n - 1] - data_mean)
        )
        denominator = np.sum((data - data_mean) ** 2)
        ac = numerator / denominator

        ac_values.append(ac)

    return pd.DataFrame({"L": l_values, "AC": ac_values})



def plot_autocorrelation(data, x_label, y_label, color="blue"):
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.plot(data.index[1:], data["AC"][1:], color=color, linewidth=2)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title('Autocorrelation Plot')
    plt.grid(True)
    return fig


def autocorrelation_plot(derivative_line):
    acf_data = acf(derivative_line)

    autocorrelation_fig = plot_autocorrelation(
        acf_data.set_index("L"), "Время", "Значение автокорреляции", "blue"
    )
    return autocorrelation_fig, acf_data


def acf_spectr_polt(acf_data):
    acf_spectr = spectr_fourier(data=acf_data["AC"], dt=1)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the Fourier spectrum
    ax.plot(acf_spectr, color='blue')
    ax.set_title('Спектр Фурье для АКФ производной линии')
    ax.set_xlabel('Частота')
    ax.set_ylabel('Амплитуда')

    return fig, acf_spectr


def ccf(datax: np.ndarray, datay: np.ndarray) -> pd.DataFrame:
    """
    Вычисляет функцию корреляции кросс-корреляции (CCF) между двумя входными массивами данных.

    Параметры:
        datax (np.ndarray): Первый входной массив данных.
        datay (np.ndarray): Второй входной массив данных.

    Возвращает:
        pd.DataFrame: DataFrame, содержащий значения задержек 'L' и соответствующие значения CCF.
    """
    if len(datax) != len(datay):
        raise ValueError("Длины входных данных не совпадают")

    n = len(datax)
    l_values = np.arange(0, n)
    x_mean = np.mean(datax)
    y_mean = np.mean(datay)
    ccf_values = (
        np.correlate(datax - x_mean, datay - y_mean, mode="full")[:n][::-1] / n
    )

    return pd.DataFrame({"L": l_values, "CCF": ccf_values})



def plot_cross_correlation(data, x_label, y_label, color="blue"):
    # fig = px.line(
    #     x=data.index[1:],
    #     y=data["CCF"][1:],
    #     labels={"x": x_label, "y": y_label},
    # )
    # fig.update_traces(line=dict(color=color, width=2))
    # fig.update_layout(
    #     xaxis_title=x_label,
    #     yaxis_title=y_label,
    #     hovermode="x",
    # )
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index[1:], data["CCF"][1:], color=color, linewidth=2)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title('Cross-Correlation Plot')
    ax.grid(True)
    return fig


def plot_fourier_spectrum(data, x_label, y_label, color="blue", title=""):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data["f"], data["|Xn|"], color=color, linewidth=2)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(True)
    return fig



def lpf( fc, m, dt):
    d = [0.35577019, 0.2436983, 0.07211497, 0.00630165]
    fact = 2 * fc * dt
    lpw = [fact] + [0] * m
    arg = fact * np.pi
    for i in range(1, m + 1):
        lpw[i] = np.sin(arg * i) / (np.pi * i)
    lpw[m] /= 2.0
    sumg = lpw[0]
    for i in range(1, m + 1):
        sum = d[0]
        arg = np.pi * i / m
        for k in range(1, 4):
            sum += 2.0 * d[k] * np.cos(arg * k)
        lpw[i] *= sum
        sumg += 2 * lpw[i]
    for i in range(m + 1):
        lpw[i] /= sumg
    return lpw


def reflect_lpf(lpw):
    reflection = []
    for i in range(len(lpw) - 1, 0, -1):
        reflection.append(lpw[i])
    reflection.extend(lpw)
    return reflection


def bsf(fc1, fc2, m, dt):
    lpw1 = reflect_lpf(lpf(fc1, m, dt))
    lpw2 = reflect_lpf(lpf(fc2, m, dt))
    bsw = [
        1.0 + lpw1[k] - lpw2[k] if k == m else lpw1[k] - lpw2[k]
        for k in range(2 * m + 1)
    ]
    return bsw


def normalize_image(image):
    """
    Нормализует заданное изображение, используя минимальное и максимальное значения, и возвращает нормализованное изображение.
    """
    min_val = np.min(image)
    max_val = np.max(image)
    normalized_image = ((image - min_val) / (max_val - min_val)) * 255
    return normalized_image



def lab6(image, rotation_angle, line_number, ds, convolution_type, dt, m, fc1, fc2):
    if image is None:
        return {'image': None}
    if isinstance(image, File):
        image = read_file(file=image)

    rotate_image = rotate_image_90_degrees(image, int(rotation_angle))

    rotate_image_line_spectr = spectr_fourier_plot(
        rotate_image, int(line_number), dt)
    
    compute_derivative_fig, derivative_line = compute_derivative_plot(
        rotate_image, int(line_number))
    
    autocorrelation_plot_fig, acf_data = autocorrelation_plot(derivative_line)

    acf_spectr_fig, acf_spectr = acf_spectr_polt(acf_data)

    # Получаем массив амплитуд спектра
    amplitudes = acf_spectr["|Xn|"]
    # Ищем максимумы
    max_amplitude = amplitudes.max()
    # Находим индекс максимальной амплитуды
    max_amplitude_index = acf_spectr["|Xn|"].idxmax()
    # Получаем значение частоты для максимальной амплитуды
    max_frequency_acf = acf_spectr["f"].iloc[max_amplitude_index]

    derivative_line_2 = compute_derivative(rotate_image[line_number + ds])

    cross_corr = ccf(derivative_line, derivative_line_2)

    cross_correlation_fig = plot_cross_correlation(cross_corr, "Время", "Значение кроскорреляции", "blue")

    ccf_spectr = spectr_fourier(data=cross_corr["CCF"], dt=1)

    ccf_spectr_fig = plot_fourier_spectrum(ccf_spectr,
        "Частота", "Амплитуда", "blue", title="Спектр Фурье для кроскорреляции двух строк",
    )

    # Получаем массив амплитуд спектра
    amplitudes_ccf = ccf_spectr["|Xn|"]

    max_amplitudes_ccf = amplitudes_ccf.max()
    # Находим индекс максимальной амплитуды
    max_amplitude_index = ccf_spectr["|Xn|"].idxmax()
    # Получаем значение частоты для максимальной амплитуды
    max_frequency_ccf = ccf_spectr["f"].iloc[max_amplitude_index]

    max_frequency = np.mean([max_frequency_acf, max_frequency_ccf])

    # Режекторный фильтр Поттера
    bsf_data = bsf(fc1, fc2, m, dt)

    filtered_image = []
    for row in rotate_image:
        filtered_row = np.convolve(row, bsf_data, mode=convolution_type)
        filtered_image.append(filtered_row)
    filtered_image = np.array(filtered_image)

    normalized_filtered_image = normalize_image(filtered_image)
    normalized_filtered_image = normalized_filtered_image.astype(np.uint16)

    filtered_derivative_line = compute_derivative(
        normalized_filtered_image[line_number]
    )
    filtered_spectr = spectr_fourier(data=filtered_derivative_line, dt=1)
    filtered_spectr_fig = plot_fourier_spectrum(
        filtered_spectr, "Частота", "Амплитуда", "blue", 
        title="Спектр Фурье для отфильтрованного изображения",
    )

    return {
        'rotate_image': NodeResult(rotate_image, ResultType.IMAGE_CV2),
        'rotate_image_line_spectr': NodeResult(rotate_image_line_spectr, ResultType.MATPLOTLIB_FIG),
        'compute_derivative_plt': NodeResult(compute_derivative_fig, ResultType.MATPLOTLIB_FIG),
        'autocorrelation_plt': NodeResult(autocorrelation_plot_fig, ResultType.MATPLOTLIB_FIG),
        'acf_spectr_plt': NodeResult(acf_spectr_fig, ResultType.MATPLOTLIB_FIG),
        "max_amplitude": NodeResult(f"Максимальная амплитуда спектра: {max_amplitude}", ResultType.STR_VALUE),
        "max_frequency_acf": NodeResult(f"Частота максимальной амплитуды: {max_frequency_acf}", ResultType.STR_VALUE),
        "cross_correlation_fig": NodeResult(cross_correlation_fig, ResultType.MATPLOTLIB_FIG),
        "ccf_spectr_fig": NodeResult(ccf_spectr_fig, ResultType.MATPLOTLIB_FIG),
        "max_amplitudes_ccf": NodeResult(f"Максимальная амплитуда спектра: {max_amplitudes_ccf}", ResultType.STR_VALUE),
        "max_frequency_ccf": NodeResult(f"Частота максимальной амплитуды: {max_frequency_ccf}", ResultType.STR_VALUE),
        "max_frequency" : NodeResult(f"Максимальная частота: {max_frequency}", ResultType.STR_VALUE),
        "normalized_filtered_image": NodeResult(normalized_filtered_image, ResultType.IMAGE_CV2),
        "filtered_spectr_fig": NodeResult(filtered_spectr_fig, ResultType.MATPLOTLIB_FIG),
    }
