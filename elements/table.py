# Формула
from dataclasses import dataclass, field
from typing import List, Optional
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

from elements.element import Element


@dataclass
class DataTable:
    data: str
    horizontal: WD_PARAGRAPH_ALIGNMENT
    vertical: WD_CELL_VERTICAL_ALIGNMENT
    colspan: int =0
    parent_col:Optional[int] =None
    parent_row:Optional[int] =None

@dataclass
class Table(Element):
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
                    for o, pr in enumerate(cell.paragraphs):
                        if o!=0:
                            pr.clear()
                    if cell.paragraphs[0].runs:
                        for p, run in enumerate(cell.paragraphs[0].runs):
                            if p != 0:  # Пропускаем первый элемент (индекс 0)
                                run.clear()
                            cell.paragraphs[0].runs[0].text=cell_data.data
                    else:
                        cell.paragraphs[0].text = cell_data.data
                    cell.paragraphs[0].alignment = cell_data.horizontal
                        
                        
                cell.vertical_alignment = cell_data.vertical
