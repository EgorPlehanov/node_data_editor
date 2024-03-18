from dataclasses import dataclass, field
from typing import List
from flet import icons, colors


@dataclass
class Folder:
    key: str = "unknown"
    name: str = "Untitled"
    icon: str = icons.QUESTION_MARK
    color: str = colors.WHITE
    obj_list: List = field(default_factory=list)