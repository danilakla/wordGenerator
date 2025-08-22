
# Формула
from dataclasses import dataclass, field
from typing import List, Optional
from docx.text.paragraph import Paragraph as DocxParagraph

from elements.element import Element

# Листинг
@dataclass
class Listing(Element):
    text: str
    caption: str
    docx_listing_paragraphs: List[DocxParagraph] = field(default_factory=list)
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""