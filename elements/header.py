# Формула
from dataclasses import dataclass, field
from typing import List, Optional
from docx.text.paragraph import Paragraph as DocxParagraph

from elements.element import Element

@dataclass
class Header(Element):
    level: int
    text: str
    children: List['Element'] = field(default_factory=list)
    docx_element: Optional[DocxParagraph] = None
    text_number_of_element: str = ""