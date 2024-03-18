from .parameter_out_value import *
from .parameter_single_value import *
from .parameter_take_value import *
from .parameter_bool_value import *
from .parameter_text_value import *
from .parameter_file_picker import *
from .parameter_dropdown_value import *



type_to_param = {
    ParameterType.OUT: OutParam,
    ParameterType.SINGLE_VALUE: SingleValueParam,
    ParameterType.TAKE_VALUE: TakeValueParam,
    ParameterType.BOOL_VALUE: BoolValueParam,
    ParameterType.TEXT_VALUE: TextValueParam,
    ParameterType.FILE_PICKER_VALUE: FilePickerParam,
    ParameterType.DROPDOWN_VALUE: DropdownValueParam,
}