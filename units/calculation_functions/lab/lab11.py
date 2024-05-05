from ..calculation_functions_typing import *
from ...data_types import File
from ..input.read import read_file

import cv2
import numpy as np



def apply_low_pass_filter(image, cutoff_frequency):
    """
    Применить фильтр Лопаса к входному изображению
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    mask = np.zeros((rows, cols, 2), np.uint8)
    mask[crow - cutoff_frequency:crow + cutoff_frequency, ccol - cutoff_frequency:ccol + cutoff_frequency] = 1

    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    
    return img_back



def apply_high_pass_filter(image, cutoff_frequency: int):
    """
    Применить фильтр Хаффмана к входному изображению
    """
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    mask = np.ones((rows, cols, 2), np.uint8)
    mask[crow - cutoff_frequency:crow + cutoff_frequency, ccol - cutoff_frequency:ccol + cutoff_frequency] = 0

    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    
    return img_back



def fun_apply_low_pass_filter(image, cutoff_frequency: int):
    """
    Применить фильтр Лапласа к входному изображению
    """
    if image is None:
        return {"low_pass_img": None}
    if isinstance(image, File):
        image = read_file(image.path)
        # image = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    low_pass_img = apply_low_pass_filter(image, cutoff_frequency)
    low_pass_img = np.clip(low_pass_img, 0, 255).astype(np.uint8)
    # low_pass_img /= np.max(low_pass_img)

    return {
        "low_pass_img": NodeResult(low_pass_img, ResultType.IMAGE_CV2),
    }



def fun_apply_high_pass_filter(image, cutoff_frequency):
    """
    Применить фильтр Хаффмана к входному изображению
    """
    if image is None:
        return {"high_pass_img": None}
    if isinstance(image, File):
        image = read_file(image.path)

    high_pass_img = apply_high_pass_filter(image, cutoff_frequency)
    # high_pass_img = np.clip(high_pass_img, 0, 255).astype(np.uint8)
    high_pass_img /= np.max(high_pass_img)

    return {
        "high_pass_img": NodeResult(high_pass_img, ResultType.IMAGE_CV2),
    }