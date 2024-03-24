from typing import Any, Callable, List
from flet import *



class StatisticParameter(Container):
    """
    Класс параметра статистики
    
    key - ключ параметра
    value - значение параметра (по умолчанию)
    name - название параметра
    values_not_shown - список значений параметра, которые не должны отображаться
    show_when - условие отображения параметра
    to_string - функция преобразования значения параметра в строку
    prefix - префикс (перед значением)
    postfix - постфикс (после значением)
    text_color - цвет текста
    bgcolor - цвет фона
    border_color - цвет границы
    tooltip - подсказка
    """
    
    def __init__(self,
        key: str,
        value: Any = '',
        name: str = None,
        values_not_shown: List = [],
        show_when: Callable = None,
        to_string: Callable = None,
        prefix: str = None,
        postfix: str = None,
        text_color: str = colors.WHITE54,
        bgcolor: str = None,
        border_color: str = None,
        tooltip: str = None,
    ):
        super().__init__()
        self.key = key
        self.value = value
        self.name = name if name is not None else key

        self.values_not_shown = values_not_shown
        self.values_not_shown.extend([str(value) for value in values_not_shown])
        self.show_when = show_when if show_when is not None else self.default_show_when
        self.to_string = to_string

        self.prefix = prefix if prefix is not None else ''
        self.postfix = postfix if postfix is not None else ''

        self.text_color = text_color
        self.bgcolor = bgcolor
        self.tooltip = tooltip
        self.border_color = border_color
        self.visible = self.show_when()
        self.content = self.create_content()
        self.set_style()


    def __str__(self) -> str:
        if self.to_string is None:
            return f"{self.name}:\u00A0{self.prefix}{self.value}{self.postfix}"
        return self.to_string(self.value)


    def set_style(self) -> None:
        """
        Устанавливает стиль параметра
        """
        self.alignment = alignment.center
        self.padding = padding.only(left = 5, right = 5)
        self.border_radius = 5
        if self.border_color is not None:
            self.border = border.all(1, self.border_color)


    def default_show_when(self) -> bool:
        """
        Дефолтное условие отображения параметра
        """
        return self.value not in self.values_not_shown and str(self.value) not in self.values_not_shown


    def create_content(self) -> Control:
        """
        Создает контент параметра
        """
        self.ref_statistics_text = Ref[Text]()
        return Text(
            ref = self.ref_statistics_text,
            value = str(self),
            selectable = True,
            expand = True,
            color = self.text_color,
            theme_style = TextThemeStyle.BODY_MEDIUM
        )
    

    def update_text(self, value: Any) -> None:
        """
        Обновляет содержимое параметра
        """
        self.value = value
        if self.show_when():
            self.visible = True
            self.ref_statistics_text.current.value = str(self)
        else:
            self.visible = False
    