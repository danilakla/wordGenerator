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
    data: str
    horizontal: WD_PARAGRAPH_ALIGNMENT
    vertical: WD_CELL_VERTICAL_ALIGNMENT
    rowspan: int = 1
    colspan: int = 1
    is_merged: bool = False
    partent_col:Optional[int] =None
    partent_row:Optional[int] =None

@dataclass
class Table:
    data: List[List[DataTable]] = field(default_factory=list)
    caption: str = ""
    docx_table: Optional[DocxTable] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None
    text_number_of_element: str = ""
    
    
    def update_docx_table(self):
        """Обновляет docx-таблицу на основе данных в `self.data`"""
        for i, row in enumerate(self.data):
            for j, cell_data in enumerate(row):
                try:
                    cell = self.docx_table.cell(i, j)
                except IndexError:
                    raise IndexError(f"Cell ({i}, {j}) is outside the table bounds")

                # Очистка существующих параграфов
                for paragraph in cell.paragraphs[1:]:
                    paragraph.clear()
                
                if not cell.paragraphs:
                    cell.add_paragraph(cell_data.data)
                else:
                    if cell.paragraphs[0].runs:
                        for run in cell.paragraphs[0].runs:
                            run.text = ""
                        cell.paragraphs[0].runs[0].text = cell_data.data
                    else:
                        cell.paragraphs[0].text = cell_data.data

                # Обновление выравнивания
                cell.paragraphs[0].alignment = cell_data.horizontal
                cell.vertical_alignment = cell_data.vertical

                # # Если ячейка объединена — применяем gridSpan/vMerge
                # if cell_data.rowspan > 1 or cell_data.colspan > 1:
                #     tc_pr = cell._element.tcPr
                #     if tc_pr is None:
                #         tc_pr = OxmlElement("w:tcPr")
                #         cell._element.insert(0, tc_pr)
                    
                #     # Горизонтальное объединение (colspan)
                #     if cell_data.colspan > 1:
                #         grid_span = OxmlElement("w:gridSpan")
                #         grid_span.set(qn("w:val"), str(cell_data.colspan))
                #         tc_pr.append(grid_span)
                    
                #     # Вертикальное объединение (rowspan)
                #     if cell_data.rowspan > 1:
                #         v_merge = OxmlElement("w:vMerge")
                #         v_merge.set(qn("w:val"), "restart")
                #         tc_pr.append(v_merge)
    


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