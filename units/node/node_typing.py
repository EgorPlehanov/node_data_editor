from enum import Enum
from random import choice



class Color(Enum):
    '''Цвет'''
    RED         = "#ff0000"
    PINK        = "#ff0072"
    PURPLE      = "#AA00FF"
    DEEP_PURPLE = "#6a00ff"
    INDIGO      = "#0026ff"
    BLUE        = "#2962FF"
    LIGHT_BLUE  = "#0091EA"
    CYAN        = "#00ddff"
    TEAL        = "#00ffdc"
    GREEN       = "#00ff69"
    LIGHT_GREEN = "#63ff00"
    LIME        = "#bdff00"
    YELLOW      = "#FFD600"
    AMBER       = "#FFAB00"
    ORANGE      = "#FF6D00"
    DEEP_ORANGE = "#DD2C00"

    def __str__(self):
        return str(self.value)
    
    @classmethod
    def random(cls):
        '''Возвращает случайное значение цвета'''
        return choice(list(cls))
