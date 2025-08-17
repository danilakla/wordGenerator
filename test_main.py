from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from docx import Document
from docx.table import Table as DocxTable, _Cell
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Cm  # Импортируем Cm для настройки ширины столбцов (если нужно)

# Класс для представления ячейки в матрице
@dataclass
class CellData:
    text: str = ""  # Текст ячейки
    rowspan: int = 1  # Количество строк, которые занимает ячейка
    colspan: int = 1  # Количество столбцов, которые занимает ячейка
    is_merged: bool = False  # Является ли ячейка частью объединенной области
    master_cell: Optional[Tuple[int, int]] = None  # Координаты "главной" ячейки объединения
    horizontal: WD_PARAGRAPH_ALIGNMENT = WD_PARAGRAPH_ALIGNMENT.LEFT
    vertical: WD_CELL_VERTICAL_ALIGNMENT = WD_CELL_VERTICAL_ALIGNMENT.TOP

# Класс для представления таблицы
@dataclass
class Table:
    data: List[List[CellData]] = field(default_factory=list)  # Матрица данных
    caption: str = ""  # Подпись таблицы
    docx_table: Optional[DocxTable] = None
    docx_caption_paragraph: Optional['Paragraph'] = None
    text_number_of_element: str = ""

    @staticmethod
    def from_docx_table(docx_table: DocxTable, caption: str = "") -> 'Table':
        """Создает объект Table из DocxTable, учитывая объединенные ячейки."""
        rows = len(docx_table.rows)
        cols = len(docx_table.columns)
        matrix = [[CellData() for _ in range(cols)] for _ in range(rows)]

        for row_idx, row in enumerate(docx_table.rows):
            for col_idx, cell in enumerate(row.cells):
                if matrix[row_idx][col_idx].is_merged:
                    continue

                colspan = cell._tc.grid_span
                rowspan = 1
                if cell._tc.vMerge:
                    rowspan = _calculate_rowspan(docx_table, row_idx, col_idx)

                matrix[row_idx][col_idx].text = cell.text.strip()
                matrix[row_idx][col_idx].rowspan = rowspan
                matrix[row_idx][col_idx].colspan = colspan
                matrix[row_idx][col_idx].horizontal = cell.paragraphs[0].alignment or WD_PARAGRAPH_ALIGNMENT.LEFT
                matrix[row_idx][col_idx].vertical = cell.vertical_alignment

                for r in range(row_idx, row_idx + rowspan):
                    for c in range(col_idx, col_idx + colspan):
                        if r == row_idx and c == col_idx:
                            continue
                        matrix[r][c].is_merged = True
                        matrix[r][c].master_cell = (row_idx, col_idx)

        return Table(data=matrix, caption=caption, docx_table=docx_table)

    def to_docx_table(self, doc: Document) -> DocxTable:
        """Создает DocxTable из матрицы данных."""
        rows = len(self.data)
        cols = len(self.data[0]) if rows > 0 else 0
        # Исправление: убираем параметр width для совместимости с python-docx < 1.0.0
        docx_table = doc.add_table(rows=rows, cols=cols)

        # Настраиваем ширину столбцов (опционально)
        for column in docx_table.columns:
            column.width = Cm(5)  # Устанавливаем ширину каждого столбца, например, 5 см

        for row_idx in range(rows):
            for col_idx in range(cols):
                cell_data = self.data[row_idx][col_idx]
                if cell_data.is_merged:
                    continue

                docx_cell = docx_table.cell(row_idx, col_idx)
                docx_cell.text = cell_data.text
                docx_cell.paragraphs[0].alignment = cell_data.horizontal
                docx_cell.vertical_alignment = cell_data.vertical

                if cell_data.rowspan > 1 or cell_data.colspan > 1:
                    end_row = row_idx + cell_data.rowspan - 1
                    end_col = col_idx + cell_data.colspan - 1
                    if end_row < rows and end_col < cols:
                        docx_cell.merge(docx_table.cell(end_row, end_col))

        self.docx_table = docx_table
        return docx_table

    def merge_cells(self, start_row: int, start_col: int, end_row: int, end_col: int) -> None:
        """Объединяет ячейки в диапазоне (start_row, start_col) - (end_row, end_col)."""
        if not (0 <= start_row <= end_row < len(self.data) and 0 <= start_col <= end_col < len(self.data[0])):
            raise ValueError("Invalid range for merging cells")

        # Обновляем матрицу
        rowspan = end_row - start_row + 1
        colspan = end_col - start_col + 1
        main_cell = self.data[start_row][start_col]

        # Проверяем, что главная ячейка не является частью другого объединения
        if main_cell.is_merged:
            raise ValueError("Main cell is part of another merge")

        # Сохраняем текст из главной ячейки
        main_cell.rowspan = rowspan
        main_cell.colspan = colspan

        # Помечаем все ячейки в диапазоне как объединенные
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                if r == start_row and c == start_col:
                    continue
                self.data[r][c].is_merged = True
                self.data[r][c].master_cell = (start_row, start_col)
                self.data[r][c].text = ""
                self.data[r][c].rowspan = 1
                self.data[r][c].colspan = 1

        # Если есть DocxTable, выполняем объединение
        if self.docx_table:
            docx_cell = self.docx_table.cell(start_row, start_col)
            docx_cell.merge(self.docx_table.cell(end_row, end_col))

    def split_cell(self, row: int, col: int, rows: int, cols: int,doc) -> None:
        """Разделяет ячейку на rows x cols под-ячеек."""
        if not (0 <= row < len(self.data) and 0 <= col < len(self.data[0])):
            raise ValueError("Invalid cell position")
        if rows < 1 or cols < 1:
            raise ValueError("Rows and columns must be positive")

        cell = self.data[row][col]
        if cell.is_merged:
            raise ValueError("Cannot split a merged cell")

        # Сбрасываем объединение, если оно есть
        if cell.rowspan > 1 or cell.colspan > 1:
            for r in range(row, row + cell.rowspan):
                for c in range(col, col + cell.colspan):
                    self.data[r][c].is_merged = False
                    self.data[r][c].master_cell = None
                    self.data[r][c].rowspan = 1
                    self.data[r][c].colspan = 1
                    self.data[r][c].text = "" if (r != row or c != col) else cell.text

        # Если требуется разделение на большее количество строк или столбцов,
        # расширяем таблицу
        if rows > cell.rowspan or cols > cell.colspan:
            self._resize_table(row, col, rows, cols)

        # Обновляем DocxTable (пересоздаем, так как python-docx не поддерживает split)
        if self.docx_table:
            new_table = self.to_docx_table(doc)
            self.docx_table = new_table

    def _resize_table(self, row: int, col: int, new_rows: int, new_cols: int) -> None:
        """Расширяет таблицу для поддержки разделения ячейки."""
        current_rows = len(self.data)
        current_cols = len(self.data[0]) if current_rows > 0 else 0

        # Вычисляем, сколько строк и столбцов нужно добавить
        add_rows = max(0, row + new_rows - current_rows)
        add_cols = max(0, col + new_cols - current_cols)

        # Добавляем новые строки
        for _ in range(add_rows):
            self.data.append([CellData() for _ in range(current_cols)])

        # Добавляем новые столбцы
        for r in range(len(self.data)):
            self.data[r].extend([CellData() for _ in range(add_cols)])

        # Обновляем размеры текущей ячейки
        self.data[row][col].rowspan = new_rows
        self.data[row][col].colspan = new_cols

        # Помечаем дополнительные ячейки как объединенные, если они входят в новую область
        for r in range(row, row + new_rows):
            for c in range(col, col + new_cols):
                if r == row and c == col:
                    continue
                self.data[r][c].is_merged = True
                self.data[r][c].master_cell = (row, col)

def _calculate_rowspan(docx_table: DocxTable, start_row: int, start_col: int) -> int:
    """Вычисляет rowspan для ячейки с вертикальным объединением."""
    rowspan = 1
    for row_idx in range(start_row + 1, len(docx_table.rows)):
        cell = docx_table.rows[row_idx].cells[start_col]
        if cell._tc.vMerge:
            rowspan += 1
        else:
            break
    return rowspan

# Пример использования
if __name__ == "__main__":
    from docx import Document

    # Создаем тестовый документ
    doc = Document()
    table = doc.add_table(rows=3, cols=3)  # Убираем параметр width
    # Настраиваем ширину столбцов (опционально)
    for column in table.columns:
        column.width = Cm(5)  # Устанавливаем ширину каждого столбца, например, 5 см
    table.cell(0, 0).text = "A1"
    table.cell(0, 1).text = "B1"
    table.cell(0, 2).text = "C1"
    table.cell(1, 0).text = "A2"
    table.cell(1, 1).merge(table.cell(2, 2))  # Объединяем B2:C3
    table.cell(1, 1).text = "Merged"

    # Парсим таблицу
    parsed_table = Table.from_docx_table(table, caption="Test Table")

    # Выводим матрицу
    print("Original table:")
    for row in parsed_table.data:
        for cell in row:
            print(f"{cell.text:10} (rs={cell.rowspan}, cs={cell.colspan}, merged={cell.is_merged})", end=" | ")
        print()
    doc.save("1modified_table.docx")

    # Объединяем ячейки A1 и B1
    parsed_table.merge_cells(0, 0, 0, 1)
    print("\nAfter merging A1 and B1:")
    for row in parsed_table.data:
        for cell in row:
            print(f"{cell.text:10} (rs={cell.rowspan}, cs={cell.colspan}, merged={cell.is_merged})", end=" | ")
        print()
    doc.save("2modified_table.docx")

    # Разделяем ячейку A2 на 2x2
    parsed_table.split_cell(1, 0, 2, 2,doc)
    print("\nAfter splitting A2 into 2x2:")
    for row in parsed_table.data:
        for cell in row:
            print(f"{cell.text:10} (rs={cell.rowspan}, cs={cell.colspan}, merged={cell.is_merged})", end=" | ")
        print()

    parsed_table.to_docx_table(doc)
    doc.save("3modified_table.docx")
