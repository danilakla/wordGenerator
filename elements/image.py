from dataclasses import dataclass
from typing import  Optional
from docx.text.paragraph import Paragraph as DocxParagraph

from elements.element import Element

@dataclass
class Image(Element):
    image_data: bytes
    caption: str
    docx_image_paragraph: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""