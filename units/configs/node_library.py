from .folder import Folder
from ..node import NodeConfig
from ..parameters import *
from ..calculation_functions import *

from typing import List
from flet import icons, colors



class NodeLibrary:
    """
    Библиотека нод с конфигурациями
    """

    @staticmethod
    def get_nodes_configs() -> List[NodeConfig]:
        return NodeLibrary.nodes_configs


    nodes_configs = [
        Folder(
            name = "Test",
            icon = icons.QUESTION_MARK,
            obj_list = [
                NodeConfig(
                    key = "test",
                    name = "Тестовая",
                    icon = icons.QUESTION_MARK,
                    function = lambda: {},
                    parameters = [
                        OutParamConfig(name = "Param 1", connect_point_color = "red"),
                        OutParamConfig(name = "Param 2", connect_point_color = "yellow"),
                        OutParamConfig(name = "Param 3", connect_point_color = "green"),
                        OutParamConfig(name = "Param 4", connect_point_color = "blue"),

                        SingleValueParamConfig(name = "Param 5"),
                        SingleValueParamConfig(name = "Param 6"),
                        SingleValueParamConfig(name = "Param 7"),
                        SingleValueParamConfig(name = "Param 8"),
                    ]
                ),

                NodeConfig(
                    key = "test3",
                    name = "Тестовая 3->2",
                    icon = icons.QUESTION_MARK,
                    function = lambda bool_val_2: {"param_1": bool_val_2},
                    parameters = [
                        OutParamConfig(name = "Param 1", connect_point_color = "green"),
                        OutParamConfig(name = "Param 2", connect_point_color = "blue"),

                        SingleValueParamConfig(name = "Param 3", connect_point_color = "red"),
                        SingleValueParamConfig(name = "Param 4", connect_point_color = "orange"),

                        BoolValueParamConfig(
                            key="bool_val_1", name="Bool tristate",
                            default_value = None, is_tristate = True
                        ),
                        BoolValueParamConfig(key="bool_val_2", name="Bool", default_value = True),

                        TextValueParamConfig(key="text", name="Text", default_value = "Test"),

                        FilePickerParamConfig(key="file_1", name="File 1"),
                        FilePickerParamConfig(
                            key="file_2", name="File 2",
                            default_value = File('D:\\POLITEH\\DATA_ANALYSIS_APP_V2\\DATA\\jpg\\grace.jpg')
                        ),

                        DropdownValueParamConfig(
                            key="dropdown_1", name="Dropdown 1",
                            # default_value = "A",
                            options = [
                                DropdownOptionConfig(key="A", text="Aaaaaaaaaa"),
                                DropdownOptionConfig(key="B", text="B"),
                                DropdownOptionConfig(key="C", text="C"),
                            ]
                        ),
                        DropdownValueParamConfig(
                            key="dropdown_2", name="Dropdown 2",
                            include_none = True,
                            options = [
                                DropdownOptionConfig(key="B", text="B"),
                                DropdownOptionConfig(key="C", text="C"),
                            ]
                        )
                    ]
                ),
            ]
        ),

        Folder(
            name = "Данные",
            icon = icons.DATA_ARRAY,
            color = colors.BLACK,
            obj_list = [
                NodeConfig(
                    key = "open_image",
                    name = "Открыть изображение",
                    icon = icons.IMAGE,
                    color = colors.BLACK,
                    width = 300,
                    function = open_image_file,
                    parameters = [
                        OutParamConfig(
                            key = "image", name = "Изображение",
                            connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                        ),

                        FilePickerParamConfig(key="image_file", name="Файл", default_value = None),
                    ]
                ),

                NodeConfig(
                    key = "image_library",
                    name = "Библиотека изображений",
                    icon = icons.IMAGE_SEARCH,
                    color = colors.BLACK,
                    width = 300,
                    # function = None,
                    parameters = [
                        OutParamConfig(
                            key = "image", name = "Image",
                            connect_point_color = colors.DEEP_PURPLE_ACCENT_700
                        ),

                        # TODO: добавить параметр выбора файла из библиотеки (сохраненной в проекте)
                    ]
                )
            ]
        ),
        
        Folder(
            name = "Математические",
            icon = icons.FUNCTIONS,
            color = colors.BLUE_700,
            obj_list = [
                NodeConfig(
                    key = "random_value",
                    name = "Случайное значение",
                    icon = icons.CASINO,
                    color = colors.BLUE_700,
                    function = random_value,
                    parameters = [
                        OutParamConfig(key = "value", name = "Value", connect_point_color = colors.BLUE_ACCENT_200),

                        SingleValueParamConfig(key = "min_value", name = "Min"),
                        SingleValueParamConfig(key = "max_value", name = "Max"),
                        SingleValueParamConfig(
                            key = "decimal_accuracy", name = "Десятичная точность",
                            decimal_accuracy = 0, default_value = 3,
                            min_value = -1, max_value = 10
                        ),
                    ]
                ),
                
                NodeConfig(
                    key = "add",
                    name = "Cумма двух чисел",
                    icon = icons.ADD,
                    color = colors.BLUE_700,
                    function = add_two_numbers,
                    parameters = [
                        OutParamConfig(key = "sum", name = "Sum", connect_point_color = colors.BLUE_ACCENT_200),

                        SingleValueParamConfig(key = "a", name = "A"),
                        SingleValueParamConfig(key = "b", name = "B"),
                    ]
                ),
            ]
        ),

        Folder(
            name = "Лабораторные",
            icon = icons.ASSIGNMENT_OUTLINED,
            obj_list = [
                Folder(
                    name = "Лабораторная 1",
                    icon = icons.LABEL,
                    color = colors.RED,
                    obj_list = [
                        NodeConfig(
                            key = "shift_image_by_constant",
                            name = "Сдвиг изображения",
                            icon = icons.IMAGE,
                            color = colors.RED,
                            function = shift_image_by_constant,
                            parameters = [
                                OutParamConfig(
                                    key="shifted_image", name="Shifted image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                
                                FilePickerParamConfig(key="image", name="Фото", default_value = None),
                                SingleValueParamConfig(key="shift_constant", name="Сдвиг", default_value=30),
                            ]
                        ),

                        NodeConfig(
                            key = "multiply_image_by_constant",
                            name = "Умножение изображения",
                            icon = icons.IMAGE,
                            color = colors.RED,
                            function = multiply_image_by_constant,
                            parameters = [
                                OutParamConfig(
                                    key="multiply_image", name="Multiply_image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(key="multiply_constant", name="Умножить на", default_value=2),
                            ]
                        ),

                        NodeConfig(
                            key = "shift_image",
                            name = "Сдвиг изображения по осям",
                            icon = icons.PHOTO_SIZE_SELECT_SMALL,
                            color = colors.RED,
                            function = shift_image,
                            parameters = [
                                OutParamConfig(
                                    key="shifted_image", name="Shifted image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="dx", name="Горизонтальный сдвиг",
                                    default_value=30, min_value=0, decimal_accuracy=0
                                ),
                                SingleValueParamConfig(
                                    key="dy", name="Вертикальный сдвиг",
                                    default_value=30, min_value=0, decimal_accuracy=0
                                ),
                            ]

                        )
                    ]
                ),

                Folder(
                    name = "Лабораторная 2",
                    icon = icons.LABEL,
                    color = colors.ORANGE,
                    obj_list = [
                        NodeConfig(
                            key = "apply_grayscale_scaling",
                            name = "Шкалирование серого цвета",
                            icon = icons.SETTINGS_BRIGHTNESS,
                            color = colors.ORANGE,
                            function = apply_grayscale_scaling,
                            parameters = [
                                OutParamConfig(
                                    key="grayscale_image", name="Grayscale image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="scale_size", name="Масштаб",
                                    min_value=0, decimal_accuracy=0, default_value=255, 
                                ),
                            ]
                        ),

                        NodeConfig(
                            key = "plot_image_histogram",
                            name = "Создание гистограммы изображения",
                            icon = icons.INSERT_CHART_OUTLINED_OUTLINED,
                            color = colors.ORANGE,
                            function = plot_image_histogram,
                            parameters = [
                                OutParamConfig(
                                    key="histogram_fig", name="Histogram",
                                    connect_point_color = colors.PINK_ACCENT_400
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                            ]
                        )
                    ]
                ),

                Folder(
                    name = "Лабораторная 3",
                    icon = icons.LABEL,
                    color = colors.YELLOW,
                    obj_list = [
                        NodeConfig(
                            key = "resize_nearest_neighbor",
                            name = "Масштабирование методом ближайшего соседа (ПАКЕТНАЯ)",
                            icon = icons.IMAGE_ASPECT_RATIO,
                            color = colors.YELLOW,
                            function = resize_nearest_neighbor,
                            parameters = [
                                OutParamConfig(
                                    key="resized_image", name="Resized image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="scale_factor", name="Масштаб",
                                    min_value=0.00001, default_value=2
                                ),
                            ]
                        ),

                        
                        NodeConfig(
                            key = "resize_nearest_neighbor_manual",
                            name = "Масштабирование методом ближайшего соседа (АЛГОРИТМ)",
                            icon = icons.IMAGE_ASPECT_RATIO,
                            color = colors.YELLOW,
                            function = resize_nearest_neighbor_manual,
                            parameters = [
                                OutParamConfig(
                                    key="resized_image", name="Resized image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="scale_factor", name="Масштаб",
                                    min_value=0.00001, default_value=2
                                ),
                            ]
                        ),
                        
                        NodeConfig(
                            key = "resize_bilinear_interpolation",
                            name = "Масштабирование методом билинейной интерполяции (ПАКЕТНАЯ)",
                            icon = icons.PHOTO_SIZE_SELECT_LARGE,
                            color = colors.YELLOW,
                            function = resize_bilinear_interpolation,
                            parameters = [
                                OutParamConfig(
                                    key="resized_image", name="Resized image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="scale_factor", name="Масштаб",
                                    min_value=0.00001, default_value=2
                                ),
                            ]
                        ),

                        NodeConfig(
                            key = "resize_bilinear_interpolation_manual",
                            name = "Масштабирование методом билинейной интерполяции (АЛГОРИТМ)",
                            icon = icons.PHOTO_SIZE_SELECT_LARGE,
                            color = colors.YELLOW,
                            function = resize_bilinear_interpolation_manual,
                            parameters = [
                                OutParamConfig(
                                    key="resized_image", name="Resized image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="scale_factor", name="Масштаб",
                                    min_value=0.00001, default_value=2
                                ),
                            ]
                        ),

                        NodeConfig(
                            key = "rotate_image_90_degrees",
                            name = "Повернуть изображение кратно 90°",
                            icon = icons.ROTATE_RIGHT,
                            color = colors.YELLOW,
                            function = rotate_image_90_degrees,
                            parameters = [
                                OutParamConfig(
                                    key="rotate_image", name="Rotated image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                DropdownValueParamConfig(
                                    key="angle", name="Угол",
                                    default_value = 90,
                                    options = [
                                        DropdownOptionConfig(key=90, text="90°"),
                                        DropdownOptionConfig(key=180, text="180°"),
                                        DropdownOptionConfig(key=270, text="270°"),
                                        DropdownOptionConfig(key=360, text="360°"),
                                    ]
                                ),
                            ]
                        ),

                        NodeConfig(
                            key = "rotate_image",
                            name = "Повернуть изображение (ПАКЕТНАЯ)",
                            icon = icons.AUTORENEW,
                            color = colors.YELLOW,
                            function = rotate_image,
                            parameters = [
                                OutParamConfig(
                                    key="rotate_image", name="Rotated image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="angle", name="Угол (°)",
                                    default_value = 90
                                ),
                            ]
                        ),

                        NodeConfig(
                            key = "rotate_image_manual",
                            name = "Повернуть изображение (АЛГОРИТМ)",
                            icon = icons.AUTORENEW,
                            color = colors.YELLOW,
                            function = rotate_image_manual,
                            parameters = [
                                OutParamConfig(
                                    key="rotate_image", name="Rotated image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="angle", name="Угол (°)",
                                    default_value = 90
                                ),
                                BoolValueParamConfig(key="resize", name="Изменять размер", default_value = False),
                            ]
                        ),
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 4",
                    icon = icons.LABEL,
                    color = colors.GREEN,
                    obj_list = [
                        NodeConfig(
                            key = "negative_transformation",
                            name = "Негативное градационное преобразование",
                            icon = icons.COMPARE,
                            color = colors.GREEN,
                            function = negative_transformation,
                            parameters = [
                                OutParamConfig(
                                    key="negative_image", name="Negative image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                            ]
                        ),
                        
                        NodeConfig(
                            key = "gamma_correction",
                            name = "Гамма-преобразование",
                            icon = icons.AUTO_FIX_HIGH,
                            color = colors.GREEN,
                            function = gamma_correction,
                            parameters = [
                                OutParamConfig(
                                    key="gamma_image", name="Gamma image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="gamma", name="Гамма", default_value = 1.0
                                ),
                                SingleValueParamConfig(
                                    key="constant", name="Константа", default_value = 1
                                )
                            ]
                        ),
                        
                        NodeConfig(
                            key = "logarithmic_transformation",
                            name = "Логарифмическое градационное преобразование",
                            icon = icons.EXPOSURE,
                            color = colors.GREEN,
                            function = logarithmic_transformation,
                            parameters = [
                                OutParamConfig(
                                    key="logarithmic_image", name="Logarithmic image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="constant", name="Константа", default_value = 1
                                )
                            ]
                        ),
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 5",
                    icon = icons.LABEL,
                    color = colors.INDIGO,
                    obj_list = [
                        NodeConfig(
                            key = "image_histogram_equalization",
                            name = "Эквализация изображения",
                            icon = icons.IMAGE,
                            color = colors.INDIGO,
                            function = image_histogram_equalization,
                            parameters = [
                                OutParamConfig(
                                    key="equalization_image", name="Equalization image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                OutParamConfig(
                                    key="original_hist", name="Original histogram",
                                    connect_point_color=colors.PINK_ACCENT_400,
                                ),
                                OutParamConfig(
                                    key="equalized_hist", name="Equalized histogram",
                                    connect_point_color=colors.PINK_ACCENT_400,
                                ),
                                
                                FilePickerParamConfig(key="image", name="Фото"),
                            ]
                        ),

                        NodeConfig(
                            key = "plot_brightness_histogram",
                            name = "Построить гистограмму яркости",
                            icon = icons.INSERT_CHART_OUTLINED_OUTLINED,
                            color = colors.INDIGO,
                            function = plot_brightness_histogram,
                            parameters = [
                                OutParamConfig(
                                    key="histogram_fig", name="Гистограмма",
                                    connect_point_color=colors.PINK_ACCENT_400
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                            ]
                        ),

                        NodeConfig(
                            key = "compute_difference_image",
                            name = "Вычислить разностное изображение",
                            icon = icons.VIEW_TIMELINE_OUTLINED,
                            color = colors.INDIGO,
                            function = compute_difference_image,
                            parameters = [
                                OutParamConfig(
                                    key="difference_image", name="Difference image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image1", name="Фото 1"),
                                FilePickerParamConfig(key="image2", name="Фото 2"),
                            ]
                        ),

                        NodeConfig(
                            key = "apply_optimal_histogram_equalization",
                            name = "Применить оптимальное градационное преобразование",
                            icon = icons.AUTO_FIX_HIGH,
                            color = colors.INDIGO,
                            function = apply_optimal_histogram_equalization,
                            parameters = [
                                OutParamConfig(
                                    key="optimal_image", name="Optimal image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                            ]
                        )
                    ]
                ),

                Folder(
                    name = "Лабораторная 6",
                    icon = icons.LABEL,
                    color = colors.PURPLE,
                    obj_list = [
                        NodeConfig(
                            key = "detect_artifacts",
                            name = "Обнаружить артефакты рентген-изображения",
                            icon = icons.QUESTION_MARK,
                            color = colors.PURPLE,
                            function = detect_artifacts,
                            parameters = [
                                OutParamConfig(
                                    key="original_spectrum", name="Original spectrum",
                                    connect_point_color=colors.PINK_ACCENT_400
                                ),
                                OutParamConfig(
                                    key="derivative_spectrum", name="Derivative spectrum",
                                    connect_point_color=colors.PINK_ACCENT_400
                                ),
                                OutParamConfig(
                                    key="autocorrelation", name="Autocorrelation",
                                    connect_point_color=colors.PINK_ACCENT_400
                                ),
                                OutParamConfig(
                                    key="crosscorrelation", name="Crosscorrelation",
                                    connect_point_color=colors.PINK_ACCENT_400
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                BoolValueParamConfig(
                                    key="is_grayscale", name="Is grayscale",
                                    default_value = True
                                ),
                            ]
                        )
                    ]
                ),

                Folder(
                    name = "Лабораторная 7",
                    icon = icons.LABEL,
                    color = colors.PINK,
                    obj_list = [
                        NodeConfig(
                            key = "add_random_noise",
                            name = "Добавить случайный шум",
                            icon = icons.BLUR_ON,
                            color = colors.PINK,
                            function = add_random_noise,
                            parameters = [
                                OutParamConfig(
                                    key="noisy_image", name="Noisy image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                OutParamConfig(
                                    key="noise", name="Noise",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="mean", name="Mean",
                                    default_value = 0
                                ),
                                SingleValueParamConfig(
                                    key="stddev", name="Stddev",
                                    default_value = 10, min_value = 0  
                                )
                            ]
                        ),

                        NodeConfig(
                            key = "add_impulse_noise",
                            name = "Добавить импульсный шум",
                            icon = icons.GRAIN,
                            color = colors.PINK,
                            function = add_impulse_noise,
                            parameters = [
                                OutParamConfig(
                                    key="noisy_image", name="Noisy image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                OutParamConfig(
                                    key="noise", name="Noise",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="salt_vs_pepper_ratio", name="Salt pepper ratio",
                                    default_value = 0.05, min_value = 0, max_value = 1
                                )

                            ]
                        ),

                        NodeConfig(
                            key = "add_mixed_noise",
                            name = "Добавить смешанный шум",
                            icon = icons.WAVES,
                            color = colors.PINK,
                            function = add_mixed_noise,
                            parameters = [
                                OutParamConfig(
                                    key="noisy_image", name="Noisy image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                OutParamConfig(
                                    key="random_noise", name="Random noise",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),
                                OutParamConfig(
                                    key="impulse_noise", name="Impulse noise",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="mean", name="Mean",
                                    default_value = 0
                                ),
                                SingleValueParamConfig(
                                    key="stddev", name="Stddev",
                                    default_value = 10, min_value = 0  
                                ),
                                SingleValueParamConfig(
                                    key="salt_vs_pepper_ratio", name="Salt pepper ratio",
                                    default_value = 0.05, min_value = 0, max_value = 1
                                )
                            ]
                        ),

                        NodeConfig(
                            key = "apply_average_filter",
                            name = "Усредняющий арифметический фильтр",
                            icon = icons.HELP,
                            color = colors.PINK,
                            function = apply_average_filter,
                            parameters = [
                                OutParamConfig(
									key="anti_noisy_image", name="Anti noisy image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="kernel_size_x", name="Kernel size X",
                                    default_value = 3, min_value = 1, decimal_accuracy=0
                                ),
                                SingleValueParamConfig(
                                    key="kernel_size_y", name="Kernel size Y",
                                    default_value = 3, min_value = 1, decimal_accuracy=0
                                )
                            ]
                        ),

                        NodeConfig(
                            key = "apply_median_filter",
                            name = "Медианный фильтр",
                            icon = icons.HELP,
                            color = colors.PINK,
                            function = apply_median_filter,
                            parameters = [
                                OutParamConfig(
                                    key="anti_noisy_image", name="Anti noisy image",
                                    connect_point_color=colors.DEEP_PURPLE_ACCENT_700
                                ),

                                FilePickerParamConfig(key="image", name="Фото"),
                                SingleValueParamConfig(
                                    key="kernel_size", name="Kernel size",
                                    default_value = 3, min_value = 1, decimal_accuracy=0
                                )
                            ]
                        )
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 8",
                    icon = icons.LABEL,
                    color = colors.BROWN,
                    obj_list = [
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 9",
                    icon = icons.LABEL,
                    color = colors.TEAL,
                    obj_list = [
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 10",
                    icon = icons.LABEL,
                    color = colors.AMBER,
                    obj_list = [
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 11",
                    icon = icons.LABEL,
                    color = colors.LIME,
                    obj_list = [
                        
                    ]
                ),

                Folder(
                    name = "Лабораторная 12",
                    icon = icons.LABEL,
                    color = colors.CYAN,
                    obj_list = [
                        
                    ]
                ),
            ]
        ),

        NodeConfig(
            key = "display_result",
            name = "Вывести результат",
            icon = icons.SEND,
            color = colors.BLACK,
            function = display_result,
            is_display_result = True,
            parameters = [
                TakeValueParamConfig(key = "result", name = "Result"),
                TextValueParamConfig(key="label", name="Label", hint_text = "Название результата..."),
            ]
        )
    ]