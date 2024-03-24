from enum import Enum



class ParameterConnectType(Enum):
    '''
    Типы подключения

    IN - входной
    OUT - выходной
    '''
    
    IN = 'in'
    OUT = 'out'

    def __str__(self):
        return self.value
    

    def __eq__(self, other):
        return (
            isinstance(other, ParameterConnectType) and self.value == other.value
            or isinstance(other, str) and self.value == other
        )
    