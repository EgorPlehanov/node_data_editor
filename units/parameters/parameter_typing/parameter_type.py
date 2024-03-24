from enum import Enum



class ParameterType(Enum):
    '''
    Типы параметров

    OUT - выходной параметр
    SINGLE_VALUE - одиночное значение
    TAKE_VALUE - взять значение
    BOOL_VALUE - булевое значение
    TEXT_VALUE - текстовое значение
    FILE_PICKER_VALUE - выбор файла
    DROPDOWN_VALUE - выпадающий список
    '''
    
    NONE = 'none'
    OUT = 'out'
    SINGLE_VALUE = 'single_value'
    TAKE_VALUE = 'take_value'
    BOOL_VALUE = 'bool_value'
    TEXT_VALUE = 'text_value'
    FILE_PICKER_VALUE = 'file_picker_value'
    DROPDOWN_VALUE = 'dropdown_value'


    def __str__(self):
        return self.value
    