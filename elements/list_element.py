# Формула
from dataclasses import dataclass, field
from typing import List
from docx.text.paragraph import Paragraph as DocxParagraph

from elements.element import Element
@dataclass
class ListElement(Element):
    items: List[str]
    list_type: str
    docx_elements: List[DocxParagraph] = field(default_factory=list)
    @property
    def list_type(self) -> str:
        return self._list_type

    @list_type.setter
    def list_type(self, value: str):
        self._list_type = value
        # Concatenate the list_type with each item in items
        self.items = [f"{value} {item}" for item in self.items]