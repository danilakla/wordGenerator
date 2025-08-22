# Формула
from dataclasses import dataclass, field
from typing import  Optional
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable

from elements.element import Element

@dataclass
class Formula(Element):
    formula: str
    caption: str
    docx_element: Optional[DocxTable] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""