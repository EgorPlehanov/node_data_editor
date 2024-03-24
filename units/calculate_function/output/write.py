import os
import cv2
import numpy as np



def get_file_path(folder_path, file_name, extension, prefix=None):
    """
    Возвращает путь к файлу с учетом его названия и расширения.
    """
    if prefix:
        file_name = f'{prefix}_{file_name}'
    if not file_name.endswith(extension):
        file_name += extension
    return os.path.join(folder_path, file_name)



def write_to_jpg_file(image, folder_path, file_name='image.jpg', prefix=None):
    """
    Сохраняет изображение по указанному пути вывода
    """
    output_path = get_file_path(folder_path, file_name, '.jpg', prefix)
    cv2.imwrite(output_path, image)

    return output_path



def write_to_bin_file(data, folder_path, file_name='image.bin', prefix=None):
    """
    Записывает данные в бинарный файл с заданным именем в указанной папке.
    """
    file_path = get_file_path(folder_path, file_name, ".bin", prefix) 
    data.astype(np.uint8).tofile(file_path) 
    return file_path



def write_to_xcr_file(data, folder_path, file_name='image', prefix=None):
    """
    Записывает данные в файл с структурой .xcr.
    """
    file_path = get_file_path(folder_path, file_name, '.xcr', prefix)

    # Преобразуем данные обратно в байты (переставляя младший и старший байты)
    data = ((data & 0xFF) << 8) | (data >> 8)

    # Записываем данные в файл с учетом формата .xcr
    with open(file_path, 'w+b') as file:
        # Пропуск заголовка (2048 байт)
        file.seek(2048)
        # Запись данных
        data.astype(np.uint16).tofile(file)

    return file_path