from dataclasses import dataclass, field
from typing import List, Optional
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

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
    @property
    def list_type(self) -> str:
        return self._list_type

    @list_type.setter
    def list_type(self, value: str):
        self._list_type = value
        # Concatenate the list_type with each item in items
        self.items = [f"{value} {item}" for item in self.items]

# Рисунок
@dataclass
class Image(Element):
    image_data: bytes
    caption: str
    docx_image_paragraph: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""
@dataclass
class DataTable:
    data:str
    horizontal:WD_PARAGRAPH_ALIGNMENT
    vertical:WD_CELL_VERTICAL_ALIGNMENT
# Таблица
@dataclass
class Table(Element):
    data: List[List[DataTable]]
    caption: str
    docx_table: Optional[DocxTable] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""

# Формула
@dataclass
class Formula(Element):
    formula: str
    caption: str
    docx_element: Optional[DocxTable] = None
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