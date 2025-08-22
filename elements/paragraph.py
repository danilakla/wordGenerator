# Формула
from dataclasses import dataclass, field
from typing import  Optional
from docx.text.paragraph import Paragraph as DocxParagraph

from elements.element import Element

@dataclass
class Paragraph(Element):
    text: str
    docx_element: Optional[DocxParagraph] = None