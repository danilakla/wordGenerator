# Формула
from dataclasses import dataclass
from typing import  Optional

from elements.element import Element

@dataclass
class UndefinedElement(Element):
    content: str
    docx_element: Optional[object] = None