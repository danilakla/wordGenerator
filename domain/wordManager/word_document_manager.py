import copy
from typing import  List, Optional
from docx import Document
from elements.element import Element
from elements.header import Header
from elements.formula import Formula
from elements.image import Image
from elements.list_element import ListElement
from elements.listing import Listing
from elements.table import Table, DataTable
from elements.paragraph import Paragraph
from domain.styleManager.style_manager import StyleManager
from domain.wordManager.tree_numbering import TreeNumbering
from io import BytesIO

from domain.parserManager.parser_word import ParserWord
from util.formula_helper import FormulaHelper


class WordDocumentManager:
    def __init__(self):
        self.tree = []
        self.formula_meneger =  FormulaHelper("resource\mml2omml.xsl")
        
    def load_document(self,doc_path: str):
        self.doc = Document(doc_path)
        self.parser_word_manager = ParserWord(self.doc)
        self.tree =self.parser_word_manager.parse_document()
        self.style_manager = StyleManager(self.doc,self.tree)
        self.numberer = TreeNumbering(self.tree)
        self.numberer.assign_numbers()
        self.doc_path = doc_path

    def save_document(self, path: Optional[str] = None):
        """Сохраняет документ."""
        self.doc.save(path or self.doc_path)

    def add_element(self, parent: Optional[Element], element: Element, after: Optional[Element] = None):
        """Добавляет элемент в дерево и документ."""
        if isinstance(element, Header):
            if parent is None:

                self.numberer.add_top_level_header(element, after_header=after)
            else:
                self.numberer.add_nested_header(parent, element, after_child=after)
        else:
            if parent is None:
                raise ValueError("Non-header elements must have a parent")
            self.numberer.add_after(parent, element)
            if not isinstance(parent,Header):
                after=parent

        self.numberer.assign_numbers()
        self._sync_element_to_doc(element, parent, after)
        self._apply_styles(element)

    def remove_element(self, element: Element):
        """Удаляет элемент из дерева и документа."""
        if isinstance(element, Header) and element.children:
            raise ValueError("Нельзя удалить заголовок с дочерними элементами")

        parent_info = self.numberer.find_parent_and_index(self.tree, element)
        if parent_info is None:
            raise ValueError("Элемент не найден в дереве")

        parent_list, index = parent_info
        parent_list.pop(index)
        self.numberer.assign_numbers()
        self.style_manager.apply_after_table_if_table_exist_delete(element)
        self._remove_element_from_doc(element)
    def update_element(self, element: Element, update_element: Element, ):
        """Update элемент  дерева и документа."""

        self.numberer.update_element_content(element,update_element)
        self._update_element_word(element)

    def _update_element_word(self, element: Element):
        if isinstance(element, Header):
            
            for i, run in enumerate(element.docx_element.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_element.runs:
                element.docx_element.runs[0].text=element.text
      
        elif isinstance(element, Paragraph):
            for i, run in enumerate(element.docx_element.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_element.runs:
                element.docx_element.runs[0].text=element.text
        elif isinstance(element, ListElement):
            # Получаем все существующие параграфы элемента
            old_paragraphs = element.docx_elements.copy()
            
            # Очищаем список параграфов элемента (но физически они остаются в документе)
            element.docx_elements.clear()
            
            # Для вставки новых элементов будем использовать последний обработанный параграф
            last_paragraph = None
            
            # Обрабатываем все элементы (старые и новые)
            for i, item in enumerate(element.items):
                if i < len(old_paragraphs):
                    # Обновляем существующий параграф
                    paragraph = old_paragraphs[i]
                    # Очищаем все runs и добавляем новый текст
                    for run in paragraph.runs:
                        run.text = ""
                    if paragraph.runs:
                        for run in paragraph.runs:
                            run.text=item
                    else:
                        paragraph.add_run(item)
                    last_paragraph = paragraph
                    element.docx_elements.append(paragraph)
                else:
                    # Добавляем новый параграф
                    if last_paragraph is not None:
                        # Вставляем после последнего обработанного параграфа
                        insert_position = last_paragraph._element
                        parent_element = insert_position.getparent()
                        insert_index = parent_element.index(insert_position) + 1
                        
                        new_paragraph = self.doc.add_paragraph(item)
                        parent_element.insert(insert_index, new_paragraph._element)
                        element.docx_elements.append(new_paragraph)
                        self.style_manager.apply_list_style(ListElement(['d'],'.',[new_paragraph]))
                        last_paragraph = new_paragraph
                    else:
                        # Если не было старых параграфов вообще
                        new_paragraph = self.doc.add_paragraph(item)
                        self.style_manager.apply_list_style(ListElement(['d'],'.',[new_paragraph]))
                        element.docx_elements.append(new_paragraph)
                        last_paragraph = new_paragraph
            
            # Удаляем лишние старые параграфы, если новых элементов меньше
            if len(element.items) < len(old_paragraphs):
                for i in range(len(element.items), len(old_paragraphs)):
                    paragraph = old_paragraphs[i]
                    if paragraph._p is not None:
                        paragraph._p.getparent().remove(paragraph._p)
        elif isinstance(element, Image):
            if element.docx_image_paragraph is not None:
                # Получаем первый run (где хранится изображение)
                runs = element.docx_image_paragraph.runs
                if runs:  # Если run существует
                    run = runs[0]  # Берём первый run (обычно там картинка)
                    run.clear()  # Удаляем старое изображение
                
                    # Пытаемся добавить новое изображение
                    try:
                        run.add_picture(BytesIO(element.image_data))
                    except Exception as e:
                        print(f"Ошибка добавления изображения: {e}")
                        # Создаём заглушку
                        from PIL import Image as PILImage
                        img = PILImage.new('RGB', (100, 100), color='gray')
                        img_byte_arr = BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        run.add_picture(BytesIO(img_byte_arr.getvalue()))
            for i, run in enumerate(element.docx_caption_paragraph.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_caption_paragraph.runs:
                element.docx_caption_paragraph.runs[0].text=element.caption
        elif isinstance(element, Table):
            from docx.oxml import OxmlElement
            docx_table = element.docx_table
            data = element.data
            new_cells: List = []
            from docx.oxml.ns import qn
            # Assume data is rectangular
            new_rows = len(data)
            new_cols = len(data[0]) if new_rows > 0 else 0
        
            old_rows = len(docx_table.rows)
            old_cols = len(docx_table.columns) if old_rows > 0 else 0
            tbl_grid = docx_table._tbl.tblGrid
            existing_widths = [int(grid_col.get(qn('w:w'), 0)) for grid_col in tbl_grid.xpath('./w:gridCol')]
            default_width = 1440  # Default width: 1 inch (1440 twips)
            proportional_width = int(sum(existing_widths) / len(existing_widths)) if existing_widths else default_width
            # Adjust columns using oxml for reliability
            if new_cols > old_cols:
                for _ in range(new_cols - old_cols):
                    # Add column to table grid
                    tbl_grid = docx_table._tbl.tblGrid
                    grid_col = OxmlElement('w:gridCol')
                    grid_col.set(qn('w:w'), str(proportional_width))
                    tbl_grid.append(grid_col)
                    # Add cell to each row
                    for row in docx_table.rows:
                        tc = OxmlElement('w:tc')
                        tc.append(OxmlElement('w:p'))  # Add paragraph to new cell
                        row._tr.append(tc)
                        new_cells.append(row.cells[-1])  # Track new cell
            elif new_cols < old_cols:
                for _ in range(old_cols - new_cols):
                    # Remove last column
                    for row in docx_table.rows:
                        row._tr.remove(row.cells[-1]._tc)
                    # Remove last grid column
                    tbl_grid = docx_table._tbl.tblGrid
                    tbl_grid.remove(tbl_grid[-1])
        
            # Adjust rows
            if new_rows > old_rows:
                for _ in range(new_rows - old_rows):
                    new_row = docx_table.add_row()
                    new_cells.extend(new_row.cells)  # Track all cells in new row
            elif new_rows < old_rows:
                for _ in range(old_rows - new_rows):
                    docx_table._tbl.remove(docx_table.rows[-1]._tr)
        
            # Ensure table grid matches new_cols
            tbl_grid = docx_table._tbl.tblGrid
            current_grid_cols = len(tbl_grid)
            if current_grid_cols < new_cols:
                for _ in range(new_cols - current_grid_cols):
                    grid_col = OxmlElement('w:gridCol')
                    grid_col.set(qn('w:w'), str(proportional_width))
                    tbl_grid.append(grid_col)
            elif current_grid_cols > new_cols:
                for _ in range(current_grid_cols - new_cols):
                    tbl_grid.remove(tbl_grid[-1])
        
            # Update cell contents
            element.update_docx_table()

            # Применяем стили к новым ячейкам
            if new_cells:  # Проверяем, что есть новые ячейки
                self.style_manager.apply_update_table_style(new_cells,element.docx_table)

           
            for i, run in enumerate(element.docx_caption_paragraph.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_caption_paragraph.runs:
                element.docx_caption_paragraph.runs[0].text=element.caption
            
        elif isinstance(element, Formula):
            if element.docx_element is not None:
                # element.docx_element is now a table with 1 row and 3 columns
                table = element.docx_element
        
                # --- Update formula in cell(0, 1) ---
                formula_cell = table.cell(0, 1)
                formula_para = formula_cell.paragraphs[0]
                # formula_para.clear()  # Custom helper needed — python-docx has no built-in clear
                # formula_run = formula_para.add_run()
                for run in formula_para.runs:
                    run._element.append(self.formula_meneger._create_omath_element(element.formula))
        
                # --- Update caption in cell(0, 2) ---
                caption_cell = table.cell(0, 2)
                caption_para = caption_cell.paragraphs[0]
                
                for i, run in enumerate(caption_para.runs):
                    if i != 0:  # Пропускаем первый элемент (индекс 0)
                        run.clear()
                if caption_para.runs:
                    caption_para.runs[0].text=f"{element.caption}"
            
            
        elif isinstance(element, Listing):
            # Сохраняем старые параграфы
            for o, pr in enumerate(element.docx_listing_paragraphs):
                if o!=0:
                    pr.clear()
            for i, run in enumerate(element.docx_listing_paragraphs[0].runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_listing_paragraphs[0].runs:
                element.docx_listing_paragraphs[0].runs[0].text=element.text
                    
            for i, run in enumerate(element.docx_caption_paragraph.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_caption_paragraph.runs:
                element.docx_caption_paragraph.runs[0].text=element.caption
                
    
    def _get_last_nested_element(self, element):
        """
        Рекурсивно находит самый последний элемент в иерархии дочерних элементов.
        Работает с элементами, которые могут содержать вложенную структуру (например, заголовки).
        """
        last_element = None
        # Проверяем сам элемент
        if hasattr(element, 'docx_table') and element.docx_table:
            last_element = element.docx_table._element
        elif hasattr(element, 'formula') and element.docx_element:
            last_element = element.docx_element._element
        elif hasattr(element, 'docx_caption_paragraph') and element.docx_caption_paragraph:
            last_element = element.docx_caption_paragraph._element
        elif hasattr(element, 'docx_elements') and element.docx_elements:
            last_element = element.docx_elements[-1]._element
        elif hasattr(element, 'docx_element') and element.docx_element:
            last_element = element.docx_element._element

        # Если у элемента есть дети, рекурсивно проверяем их
        if hasattr(element, 'children') and element.children:
            for child in element.children:
                child_last = self._get_last_nested_element(child)
                if child_last is not None:
                    last_element = child_last

        return last_element
    def _sync_element_to_doc(self, element: Element, parent: Optional[Element], after: Optional[Element]):
        """Синхронизирует отдельный элемент с документом."""
        # Определяем позицию вставки
        
        insert_position = None
        if after and not isinstance(element,Header):
            
            if hasattr(after, 'docx_table') and after.docx_table:
                insert_position = after.docx_table._element
            elif hasattr(after, 'formula') and after.docx_element:
                insert_position = after.docx_element._element
            elif hasattr(after, 'docx_caption_paragraph') and after.docx_caption_paragraph:
                insert_position = after.docx_caption_paragraph._element
            elif hasattr(after, 'docx_elements') and after.docx_elements:
                insert_position = after.docx_elements[-1]._element
            elif hasattr(after, 'docx_element') and after.docx_element:
                insert_position = after.docx_element._element
        elif parent and isinstance(parent, Header) and parent.docx_element and isinstance(after,Header):
            insert_position = parent.docx_element._element
            for child in parent.children:
                if child == after:
                    insert_position = self._get_last_nested_element(child)
                    break
        elif parent and isinstance(parent, Header) and parent.docx_element:
            insert_position = parent.docx_element._element
            for child in parent.children:
                
                if child == element:
                    index  = parent.children.index(child)-1
                    if  index > -1 and isinstance(parent.children[index],Header):
                       insert_position = self._get_last_nested_element(parent.children[index])
                    elif index> -1 and not isinstance(parent.children[index],Header):
                        break
                    else:
                        insert_position = parent.docx_element._element
                    break
                if hasattr(child, 'docx_table') and child.docx_table:
                    insert_position = child.docx_table._element
                elif hasattr(child, 'formula') and child.docx_element:
                    insert_position = child.docx_element._element
                elif hasattr(child, 'docx_caption_paragraph') and child.docx_caption_paragraph:
                    insert_position = child.docx_caption_paragraph._element
                elif hasattr(child, 'docx_elements') and child.docx_elements:
                    insert_position = child.docx_elements[-1]._element
                elif hasattr(child, 'docx_element') and child.docx_element:
                    insert_position = child.docx_element._element
        elif isinstance(element, Header) and isinstance(after,Header) and parent is None:
            for child in self.tree:
                if child == after:
                    insert_position = self._get_last_nested_element(child)
                    break
        # Добавляем элемент в документ
        if isinstance(element, Header):
            style_name = f'Heading {element.level}'
            if style_name not in [s.name for s in self.doc.styles]:
                self.doc.styles.add_style(style_name, 1)
            p = self.doc.add_heading(element.text, level=element.level)
            element.docx_element = p
            element.docx_element.style = f'Heading {element.level}'
            if element.level==1:
                element.docx_element.paragraph_format.page_break_before=True
        elif isinstance(element, Paragraph):
            p = self.doc.add_paragraph(element.text)
            element.docx_element = p
        elif isinstance(element, ListElement):
            element.docx_elements = [self.doc.add_paragraph(item) for item in element.items]
        elif isinstance(element, Image):
            element.docx_image_paragraph = self.doc.add_paragraph()
            run = element.docx_image_paragraph.add_run()
            try:
                run.add_picture(BytesIO(element.image_data))
            except:
                # Заглушка: создаем временное изображение
                from PIL import Image as PILImage
                img = PILImage.new('RGB', (100, 100), color='gray')
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                run.add_picture(BytesIO(img_byte_arr.getvalue()))
            element.docx_caption_paragraph = self.doc.add_paragraph(element.caption)
        elif isinstance(element, Table):
            element.docx_caption_paragraph = self.doc.add_paragraph(element.caption)
            element.docx_table = self.doc.add_table(rows=len(element.data), cols=len(element.data[0]))
            for i, row in enumerate(element.data):
                for j, cell in enumerate(row):
                    element.docx_table.rows[i].cells[j].text = cell.data
        elif isinstance(element, Formula):

            # Create table with 1 row and 3 columns
            table = self.doc.add_table(rows=1, cols=3)

            # Remove borders if you don't want them
  

            # Column 2 (index 1) - formula centered
            formula_cell = table.cell(0, 1)
            formula_para = formula_cell.paragraphs[0]
            formula_run = formula_para.add_run()
            formula_run._element.append(self.formula_meneger._create_omath_element(element.formula))

            # Column 3 (index 2) - caption right-aligned
            caption_cell = table.cell(0, 2)
            caption_para = caption_cell.paragraphs[0]
            caption_para.text=(f"{element.caption}")

            # Save table reference if needed
            element.docx_element = table
            element.docx_caption_paragraph=caption_para

            
            
        elif isinstance(element, Listing):
            element.docx_listing_paragraphs = [self.doc.add_paragraph(element.text)]
            element.docx_caption_paragraph = self.doc.add_paragraph(element.caption)
            
        # Перемещаем элемент в нужную позицию
        main_element = None
        if hasattr(element, 'docx_table') and element.docx_table:
            main_element = element.docx_table._element
        if hasattr(element,"formula")and  element.docx_element:
            main_element = element.docx_element._element
        elif hasattr(element, 'docx_listing_paragraphs') and element.docx_listing_paragraphs:
            main_element = [p._element for p in element.docx_listing_paragraphs]
        elif hasattr(element, 'docx_image_paragraph') and element.docx_image_paragraph:
            main_element = element.docx_image_paragraph._element
        elif hasattr(element, 'docx_elements') and element.docx_elements:
            main_element = [p._element for p in element.docx_elements]
        elif hasattr(element, 'docx_element') and element.docx_element:
            main_element = element.docx_element._element

        if insert_position is not None and main_element is not None:
            # Вставляем после insert_position
            parent_element = insert_position.getparent()
            insert_index = parent_element.index(insert_position) + 1
            if isinstance(element,Listing) or isinstance(element,ListElement):
                for main_elemend in main_element:
                    parent_element.insert(insert_index, main_elemend)
                    insert_index += 1
            else:
                parent_element.insert(insert_index, main_element)
   
        if isinstance(element, Table) and element.docx_caption_paragraph:
            # Подпись таблицы перед таблицей
            parent_element = element.docx_table._element.getparent()
            table_index = parent_element.index(element.docx_table._element)
            parent_element.insert(table_index, element.docx_caption_paragraph._element)
        elif isinstance(element, (Image, Listing)) and element.docx_caption_paragraph:
            # Подпись изображения и листинга после основного элемента
            main_element = element.docx_image_paragraph._element if isinstance(element, Image) else element.docx_listing_paragraphs[-1]._element
            parent_element = main_element.getparent()
            main_index = parent_element.index(main_element) + 1
            parent_element.insert(main_index, element.docx_caption_paragraph._element)
    def _sync_move_to_doc(self, element: Element, parent: Optional[Element], after: Optional[Element], main_el: Optional[Header],stop_el:Optional[Header]):
        """Синхронизирует отдельный элемент с документом."""
        # Определяем позицию вставки
        
        insert_position = None
        if after and not isinstance(element,Header):
            
            if hasattr(after, 'docx_table') and after.docx_table:
                insert_position = after.docx_table._element
            elif hasattr(after, 'formula') and after.docx_element:
                insert_position = after.docx_element._element
            elif hasattr(after, 'docx_caption_paragraph') and after.docx_caption_paragraph:
                insert_position = after.docx_caption_paragraph._element
            elif hasattr(after, 'docx_elements') and after.docx_elements:
                insert_position = after.docx_elements[-1]._element
            elif hasattr(after, 'docx_element') and after.docx_element:
                insert_position = after.docx_element._element
        elif parent and isinstance(parent, Header) and parent.docx_element and isinstance(after,Header):
            insert_position = parent.docx_element._element
            for child in parent.children:
                if child == after:
                    insert_position = self._get_last_nested_element(child)
                    break
        elif parent and isinstance(parent, Header) and parent.docx_element:
            insert_position = parent.docx_element._element
            for child in parent.children:
                
                if child == element:
                    index  = parent.children.index(child)-1
                    if  index > -1 and isinstance(parent.children[index],Header):
                       insert_position = self._get_last_nested_element(parent.children[index])
                    elif index> -1 and not isinstance(parent.children[index],Header):
                        break
                    else:
                        insert_position = parent.docx_element._element
                    break
                if hasattr(child, 'docx_table') and child.docx_table:
                    insert_position = child.docx_table._element
                elif hasattr(child, 'formula') and child.docx_element:
                    insert_position = child.docx_element._element
                elif hasattr(child, 'docx_caption_paragraph') and child.docx_caption_paragraph:
                    insert_position = child.docx_caption_paragraph._element
                elif hasattr(child, 'docx_elements') and child.docx_elements:
                    insert_position = child.docx_elements[-1]._element
                elif hasattr(child, 'docx_element') and child.docx_element:
                    insert_position = child.docx_element._element
        elif isinstance(element, Header) and isinstance(after,Header) and parent is None:
            for child in self.tree:
                if child == after:
                    insert_position = self._get_last_nested_element(child)
                    break
        main_element = None
        if hasattr(element, 'docx_table') and element.docx_table:
            main_element = element.docx_table._element
        elif hasattr(element, 'formula') and element.docx_element:
            main_element = element.docx_element._element
        elif hasattr(element, 'docx_listing_paragraphs') and element.docx_listing_paragraphs:
            main_element = [p._element for p in element.docx_listing_paragraphs]
        elif hasattr(element, 'docx_image_paragraph') and element.docx_image_paragraph:
            main_element = element.docx_image_paragraph._element
        elif hasattr(element, 'docx_elements') and element.docx_elements:
            main_element = [p._element for p in element.docx_elements]
        elif hasattr(element, 'docx_element') and element.docx_element:
            main_element = element.docx_element._element
        if isinstance(element,Header):
            style_name = f'Heading {element.level}'
            if style_name not in [s.name for s in self.doc.styles]:
                self.doc.styles.add_style(style_name, 1)
            element.docx_element.style = f'Heading {element.level}'
        if isinstance(element,Header) and element.level==1 and  element.docx_element.paragraph_format.page_break_before==False:
                element.docx_element.paragraph_format.page_break_before=True
        if isinstance(element,Header) and element.level>1 and  element.docx_element.paragraph_format.page_break_before==True:
                element.docx_element.paragraph_format.page_break_before=False

        if insert_position is not None and main_element is not None:
            # Вставляем после insert_position
            parent_element = insert_position.getparent()
            insert_index = parent_element.index(insert_position) + 1
            if isinstance(element,Listing) or isinstance(element,ListElement):
                for main_elemend in main_element:
                    parent_element.insert(insert_index, main_elemend)
                    insert_index += 1
            else:
                parent_element.insert(insert_index, main_element)
                # self.safe_insert_after(parent_element, insert_position, main_element)
        if isinstance(element,Paragraph) or isinstance(element, ListElement):
            self.style_manager.apply_after_table_if_table_exist(element)
        if isinstance(element, Table) and element.docx_caption_paragraph:
            # Подпись таблицы перед таблицей
            parent_element = element.docx_table._element.getparent()
            table_index = parent_element.index(element.docx_table._element)
            parent_element.insert(table_index, element.docx_caption_paragraph._element)
            self.style_manager.apply_after_table_if_table_exist(element)
        elif isinstance(element, (Image, Listing)) and element.docx_caption_paragraph:
            # Подпись изображения и листинга после основного элемента
            main_element = element.docx_image_paragraph._element if isinstance(element, Image) else element.docx_listing_paragraphs[-1]._element
            parent_element = main_element.getparent()
            main_index = parent_element.index(main_element) + 1
            parent_element.insert(main_index, element.docx_caption_paragraph._element)
        if main_el is not None:
            if isinstance(element,Header) and element.children:
                self._sync_move_to_doc(element.children[0],element,None,element,stop_el)
            elif not isinstance(element,Header):
                 index = main_el.children.index(element)
                 next_element = main_el.children[index + 1] if index + 1 < len(main_el.children) else None
                 if next_element is not None and not isinstance(next_element,Header):
                    self._sync_move_to_doc(next_element,None,element,main_el,stop_el)
                 elif next_element is not None and  isinstance(next_element,Header):
                    prev_header = self.find_previous_header(next_element,main_el)
                    self._sync_move_to_doc(next_element,main_el,prev_header,main_el,stop_el)

                 elif next_element is None:
                     parent_of_header =None 
                     while True:               
                        parent_of_header = self.numberer.find_parent_element(self.tree,main_el)
                        if parent_of_header is stop_el or parent_of_header is None:
                                break
                        index = parent_of_header.children.index(main_el)
                        next_element = parent_of_header.children[index + 1] if index + 1 < len(parent_of_header.children) else None
                        if  next_element is None:
                            main_el = parent_of_header
                        else:
                            break
                     if parent_of_header is not  stop_el:
                        main_el = parent_of_header
                        prev_header = self.find_previous_header(next_element,main_el)
                        self._sync_move_to_doc(next_element,main_el,prev_header,main_el,stop_el)
                        
            elif isinstance(element,Header) and not element.children:
                while True:
                    parent_of_header = self.numberer.find_parent_element(self.tree,element)
                    if parent_of_header is stop_el or parent_of_header is None:
                        break
                    index = parent_of_header.children.index(element)
                    next_element = parent_of_header.children[index + 1] if index + 1 < len(parent_of_header.children) else None
                    if  next_element is None:
                        main_el = parent_of_header
                    else:
                        break
                if parent_of_header is not  stop_el:
                    main_el = parent_of_header
                    prev_header = self.find_previous_header(next_element,main_el)
                    self._sync_move_to_doc(next_element,main_el,prev_header,main_el,stop_el)
                     
             
    def get_next_element(self,parent, child):
        index = parent.children.index(child)
        return parent.children[index + 1] if index + 1 < len(parent.children) else None

    def climb_to_next_element(self,start_el, stop_el):
        current = start_el
        while True:
            parent = self.numberer.find_parent_element(self.tree, current)
            if parent is stop_el:
                return None, parent
            next_el = self.get_next_element(parent, current)
            if next_el is None:
                current = parent
            else:
                return next_el, parent

    def move_with_prev_header(self,next_el, main_el):
        prev_header = self.find_previous_header(next_el, main_el)
        self._sync_move_to_doc(next_el, main_el, prev_header, main_el,None)

    def find_previous_header(self,current_header: Header, parent: Header) -> Optional[Header]:
    # Ищем текущий заголовок среди детей родителя
        for i, child in enumerate(parent.children):
            if child == current_header:
                # Идем в обратном порядке от текущего индекса
                for j in range(i - 1, -1, -1):
                    candidate = parent.children[j]
                    if isinstance(candidate, Header) and candidate.level <= current_header.level:
                        return candidate
                return None  # Ничего не нашли
        return None

    def remove_header(self, element: Element, force: bool = False):
        """Удаляет заголовок из документа. Если force=True, удаляет заголовок и его дочерние элементы, иначе удаляет только если нет дочерних элементов."""
        if isinstance(element, Header) and element.docx_element:
            if force or not element.docx_element._element.getchildren():
                element.docx_element._element.getparent().remove(element.docx_element._element)
    def _remove_element_from_doc(self, element: Element):
        """Удаляет элемент из документа."""
        if isinstance(element, Header) and element.docx_element:
            element.docx_element._element.getparent().remove(element.docx_element._element)
        elif isinstance(element, Paragraph) and element.docx_element:
            element.docx_element._element.getparent().remove(element.docx_element._element)
        elif isinstance(element, Image):
            if element.docx_image_paragraph:
                element.docx_image_paragraph._element.getparent().remove(element.docx_image_paragraph._element)
            if element.docx_caption_paragraph:
                element.docx_caption_paragraph._element.getparent().remove(element.docx_caption_paragraph._element)
        elif isinstance(element, Table):
            if element.docx_caption_paragraph:
                element.docx_caption_paragraph._element.getparent().remove(element.docx_caption_paragraph._element)
            if element.docx_table:
                element.docx_table._element.getparent().remove(element.docx_table._element)
        elif isinstance(element, Formula):
            if element.docx_element:
                element.docx_element._element.getparent().remove(element.docx_element._element)
        elif isinstance(element, Listing):
            for para in element.docx_listing_paragraphs:
                para._element.getparent().remove(para._element)
            if element.docx_caption_paragraph:
                element.docx_caption_paragraph._element.getparent().remove(element.docx_caption_paragraph._element)
        elif isinstance(element, ListElement):
            for para in element.docx_elements:
                para._element.getparent().remove(para._element)

    def _apply_styles(self, element: Element):
        """Применяет стили к элементу."""
        if isinstance(element, Header):
            self.style_manager.apply_header_style(element)
        elif isinstance(element, Image):
            self.style_manager.apply_image_style(element)
        elif isinstance(element, Table):
            self.style_manager.apply_table_style(element)
        elif isinstance(element, Formula):
            self.style_manager.apply_formula_style(element)
        elif isinstance(element, Listing):
            self.style_manager.apply_listing_style(element)
        elif isinstance(element, Paragraph):
            self.style_manager.apply_paragraph_style(element)
        elif isinstance(element, ListElement):
            self.style_manager.apply_list_style(element)

 
    
  
    def move_element_word(self, parent: Element, element: Element, after:Element =None):
        
        if isinstance(element,Header):
            self.numberer.adjust_header_levels(parent,element)
        
        self.numberer.move_element(parent,element,after)
        
        if not isinstance(element,Header) and not isinstance(parent,Header):
            after=parent
        if isinstance(element,Header):
            self._sync_move_to_doc(element,parent,after,element,parent)
        else:
            self._sync_move_to_doc(element,parent,after,None,None)
    
            
            

