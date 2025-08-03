from dataclasses import dataclass, field
import re
from typing import List, Optional
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from docx.oxml.ns import qn, nsmap
from lxml import etree


class Element:
    pass

# Заголовок
@dataclass
class Header(Element):
    level: int
    text: str
    children: List['Element'] = field(default_factory=list)
    docx_element: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Параграф
@dataclass
class Paragraph(Element):
    text: str
    docx_element: Optional[DocxParagraph] = None

# Список
@dataclass
class ListElement(Element):
    items: List[str]
    list_type: str
    docx_elements: List[DocxParagraph] = field(default_factory=list)

# Рисунок
@dataclass
class Image(Element):
    image_data: bytes
    caption: str
    docx_image_paragraph: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Таблица
@dataclass
class Table(Element):
    data: List[List[str]]
    caption: str
    docx_table: Optional[DocxTable] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Формула
@dataclass
class Formula(Element):
    formula: str
    caption: str
    docx_element: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Листинг
@dataclass
class Listing(Element):
    text: str
    caption: str
    docx_listing_paragraphs: List[DocxParagraph] = field(default_factory=list)
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Неизвестный элемент
@dataclass
class UndefinedElement(Element):
    content: str
    docx_element: Optional[object] = None