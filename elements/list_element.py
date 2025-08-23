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
