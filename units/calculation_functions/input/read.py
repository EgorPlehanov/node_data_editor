from ..calculation_functions_typing import *
from ...data_types import File

import cv2
import numpy as np



def read_jpg_image(file_path):
    """
    Чтение jpg изображения
    """
    return cv2.imread(file_path)



def read_xcr_file(file_path, shape=(1024, 1024)):
    """
    Читает файл XCR и возвращает данные в виде массива NumPy с указанной формой
    """
    with open(file_path, 'rb') as file:
        # Пропуск заголовка (2048 байт)
        file.seek(2048)
        # Чтение данных (shape[0] * shape[1] двухбайтовых, беззнаковых целочисленных значений)
        data = np.fromfile(file, dtype=np.uint16, count=shape[0]*shape[1])

    # Меняем местами младший и старший байты
    data = ((data & 0xff) << 8) | (data >> 8)
    # Преобразуем данные в массив с указанной формой
    return data.reshape(shape)



def read_bin_file(file_path, shape=(1024, 1024)):
    """
    Читает бинарный файл и возвращает данные в виде массива NumPy.
    """
    # TODO: НЕ РАБОТАЕТ!
    return np.fromfile(file_path, dtype=np.uint8).reshape(shape)



def read_file(file: File | str = None):
    '''
    Чтение данных из файлов
    '''
    read_data = {
        'jpg': read_jpg_image,
        'jpg': read_jpg_image, 
        "jpeg": read_jpg_image,
        "png": read_jpg_image,
        "bmp": read_jpg_image,
        "gif": read_jpg_image,
        "xcr": read_xcr_file,
        "bin": read_bin_file
    }
    
    if not isinstance(file, File):
        file = File(path=file)
    try:
        if file.extension in read_data:
            return read_data[file.extension](file.path)
        else: 
            raise ValueError(f"Формат {file.extension} не поддерживается")
    except Exception as e:
        raise ValueError(f"При чтении файла '{file.formatted_name}' произошла ошибка: {str(e)}")
    


def open_image_file(image_file: File):
    """
    Открывает изображение из файла
    """
    if image_file is None:
        return {'image': None}
    if isinstance(image_file, File):
        image_file = read_file(file=image_file)
    return {
        'image': NodeResult(image_file, ResultType.IMAGE_CV2),
    }