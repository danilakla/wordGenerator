# Создание таблицы
from docx import Document

from elements import DataTable, Table

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
# Создание таблицы
# Создание таблицы
doc = Document()
table = doc.add_table(rows=3, cols=3)
docx_table = Table(docx_table=table, caption="Пример")

# Заполнение данных
for i in range(3):
    for j in range(3):
        cell = docx_table.docx_table.cell(i, j)
        cell.text = f"{i+1}-{j+1}"

# Обновление внутреннего представления
docx_table._build_layout_grid()
docx_table._sync_data_with_grid()

# Объединение ячеек
docx_table.merge_cells(0, 0, 1, 1)

# Разделение ячейки
docx_table.split_cell(2, 2, 2, 2)

# Обновление документа
docx_table.update_docx_table()

# Сохранение
doc.save("table_example.docx")