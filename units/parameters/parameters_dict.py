from .parameter_typing.parameter_interface import ParameterType

from .parameter_bool_value import BoolValueParam
from .parameter_dropdown_value import DropdownValueParam
from .parameter_file_picker import FilePickerParam
from .parameter_out_value import OutParam
from .parameter_single_value import  SingleValueParam
from .parameter_take_value import TakeValueParam
from .parameter_text_value import TextValueParam



"""
Словарь соответствия типов параметров к параметрам
"""
type_to_param = {
    ParameterType.OUT: OutParam,
    ParameterType.SINGLE_VALUE: SingleValueParam,
    ParameterType.TAKE_VALUE: TakeValueParam,
    ParameterType.BOOL_VALUE: BoolValueParam,
    ParameterType.TEXT_VALUE: TextValueParam,
    ParameterType.FILE_PICKER_VALUE: FilePickerParam,
    ParameterType.DROPDOWN_VALUE: DropdownValueParam,
}