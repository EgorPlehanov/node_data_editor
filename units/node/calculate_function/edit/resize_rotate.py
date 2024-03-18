from ....parameters.parameter_typing import File
from ..calculate_function_typing import *
from ..input.read import read_file
import numpy as np
import cv2



def resize_nearest_neighbor(image, scale_factor: float):
    """
    (ПАКЕТНАЯ) Меняет размер изображения с использованием метода ближайшего соседа
    """
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)
    return {
        "resized_image": NodeResult(
            cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_NEAREST),
            ResultType.IMAGE_CV2
        ),
    }



def resize_nearest_neighbor_manual(image, scale_factor: float):
    """
    (АЛГОРИТМ) Меняет размер изображения с использованием метода ближайшего соседа
    """
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    
    new_height, new_width = int(image.shape[0] * scale_factor), int(image.shape[1] * scale_factor)
    new_image = np.empty((new_height, new_width, image.shape[2]), dtype=image.dtype)
    for i in range(new_height):
        for j in range(new_width):
            old_y, old_x = min(int(i / scale_factor), image.shape[0] - 1), min(int(j / scale_factor), image.shape[1] - 1)
            new_image[i, j] = image[old_y, old_x]
    return {
        "resized_image": NodeResult(new_image, ResultType.IMAGE_CV2),
    }



def resize_bilinear_interpolation(image, scale_factor: float):
    """
    (ПАКЕТНАЯ) Меняет размер изображения с использованием метода билинейной интерполяции
    """
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)
    return {
        "resized_image": NodeResult(
            cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR),
            ResultType.IMAGE_CV2
        ),
    }



def resize_bilinear_interpolation_manual(image, scale_factor: float):
    """
    (АЛГОРИТМ) Меняет размер изображения с использованием метода билинейной интерполяции
    """
    if image is None:
        return {"resized_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    new_height, new_width = int(image.shape[0] * scale_factor), int(image.shape[1] * scale_factor)
    new_image = np.empty((new_height, new_width, image.shape[2]), dtype=image.dtype)
    for i in range(new_height):
        for j in range(new_width):
            y, x = i / scale_factor, j / scale_factor
            x1, y1 = int(x), int(y)
            x2, y2 = min(x1 + 1, image.shape[1] - 1), min(y1 + 1, image.shape[0] - 1)
            dx, dy = x - x1, y - y1
            new_image[i, j] = (1 - dx) * (1 - dy) * image[y1, x1] + dx * (1 - dy) * image[y1, x2] + (1 - dx) * dy * image[y2, x1] + dx * dy * image[y2, x2]
    return {
        "resized_image": NodeResult(new_image, ResultType.IMAGE_CV2),
    }



def rotate_image(image, angle: float = 90):
    """
    (ПАКЕТНАЯ) Поворачивает изображение на заданный угол
    """
    if image is None:
        return {"rotate_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    height, width = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    return {
        "rotate_image": NodeResult(rotated_image, ResultType.IMAGE_CV2),
    }



def rotate_image_90_degrees(image, angle: int):
    """
    Поворачивает растровое изображение на угол, кратный 90 градусам.
    """
    if image is None:
        return {"rotate_image": None}
    if isinstance(image, File):
        image = read_file(image.path)
    print(angle)
    num_rotations = int(angle) // 90
    rotated_image = np.rot90(image, k=num_rotations)
    return {
        "rotate_image": NodeResult(rotated_image, ResultType.IMAGE_CV2),
    }




def rotate_image_manual(image, angle: float, resize: bool = False):
    """
    (АЛГОРИТМ) Поворачивает изображение на заданный угол
    """
    if image is None:
        return {"rotate_image": None}
    if isinstance(image, File):
        image = read_file(image.path)

    if angle % 90 == 0:
        return rotate_image_90_degrees(image, angle)

    # Преобразование угла в радианы
    angle_rad = np.radians(angle)

    # Получение размеров изображения
    height, width = image.shape[:2]

    if resize:
        # Рассчитываем новые размеры изображения после поворота
        new_width = int(np.ceil(np.abs(width * np.cos(angle_rad)) + np.abs(height * np.sin(angle_rad))))
        new_height = int(np.ceil(np.abs(width * np.sin(angle_rad)) + np.abs(height * np.cos(angle_rad))))

        # Создаем пустое изображение с новыми размерами
        rotated_image = np.zeros(
            (new_height, new_width, image.shape[2] if len(image.shape) == 3 else 1),
            dtype=image.dtype
        )

    else:
        # Используем те же размеры изображения
        rotated_image = np.zeros_like(image)

    # Рассчитываем координаты центра исходного изображения
    center_x, center_y = width // 2, height // 2

    # Проходим по каждому пикселю в новом изображении
    for y in range(rotated_image.shape[0]):
        for x in range(rotated_image.shape[1]):
            # Рассчитываем координаты пикселя в исходном изображении после поворота
            original_x = int((x - rotated_image.shape[1] / 2) * np.cos(angle_rad) - (y - rotated_image.shape[0] / 2) * np.sin(angle_rad) + center_x)
            original_y = int((x - rotated_image.shape[1] / 2) * np.sin(angle_rad) + (y - rotated_image.shape[0] / 2) * np.cos(angle_rad) + center_y)

            # Проверяем, находится ли пиксель в пределах исходного изображения
            if 0 <= original_x < width and 0 <= original_y < height:
                # Копируем значение пикселя из исходного изображения в новое
                rotated_image[y, x] = image[original_y, original_x]

    return {
        "rotate_image": NodeResult(rotated_image, ResultType.IMAGE_CV2),
    }