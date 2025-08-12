
from typing import  Optional
from docx import Document
from docx.text.paragraph import Paragraph 
from elements import Element, Header, Image, Table, Formula, Listing, Paragraph, ListElement
from formula_helper import FormulaHelper
from maind import print_tree
from style_manager import StyleManager
from tree_numbering import TreeNumbering
from io import BytesIO



class WordDocumentManager:
    def __init__(self, doc_path: str):
        self.doc = Document(doc_path)
        self.tree = []
        self.formula_meneger =  FormulaHelper("mml2omml.xsl")
        self.numberer = TreeNumbering(self.tree)
        self.style_manager = StyleManager(self.doc,self.tree)
        self.doc_path = doc_path

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
        self._remove_element_from_doc(element)
    def update_element(self, element: Element, update_element: Element, ):
        """Update элемент  дерева и документа."""

        self.numberer.update_element_content(element,update_element)
        self._update_element_word(element)

    def _update_element_word(self, element: Element):
        if isinstance(element, Header):
            element.docx_element.runs[0].text = element.text
        elif isinstance(element, Paragraph):
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
                        paragraph.runs[0].text = item
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
            element.docx_caption_paragraph.runs[0].text = element.caption
        elif isinstance(element, Table):
            # Сохраняем ссылку на старую таблицу
            old_table = element.docx_table
            
            # Создаем новую таблицу
            new_table = self.doc.add_table(rows=len(element.data), cols=len(element.data[0]))
            
            # Заполняем новую таблицу данными
            for i, row in enumerate(element.data):
                for j, cell in enumerate(row):
                    new_table.cell(i, j).text = cell
            
            insert_position = old_table._element
            
            parent_element = insert_position.getparent()
            insert_index = parent_element.index(insert_position)+1
            parent_element.insert(insert_index,new_table._element)
            if old_table is not None and old_table._tbl is not None:
                old_table._tbl.getparent().remove(old_table._tbl)            
            # Обновляем ссылку на таблицу в элементе
            element.docx_table = new_table
            element.docx_caption_paragraph.text=element.caption
            
        elif isinstance(element, Formula):
            if element.docx_element is not None:
                # element.docx_element is now a table with 1 row and 3 columns
                table = element.docx_element
        
                # --- Update formula in cell(0, 1) ---
                formula_cell = table.cell(0, 1)
                formula_para = formula_cell.paragraphs[0]
                formula_para.clear()  # Custom helper needed — python-docx has no built-in clear
                formula_run = formula_para.add_run()
                formula_run._element.append(self.formula_meneger._create_omath_element(element.formula))
        
                # --- Update caption in cell(0, 2) ---
                caption_cell = table.cell(0, 2)
                caption_para = caption_cell.paragraphs[0]
                caption_para.text = f"{element.caption}"
            
            
        elif isinstance(element, Listing):
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn

            # Сохраняем старые параграфы
            old_paragraphs = element.docx_listing_paragraphs.copy()

            # Создаем новые параграфы с рамкой
            new_paragraphs = []
            for line in element.text.split('\n'):
                new_paragraph = self.doc.add_paragraph(line)

                # Настраиваем границы
                p_pr = new_paragraph._element.get_or_add_pPr()
                p_bdr = OxmlElement('w:pBdr')

                for border_name in ['top', 'left', 'bottom', 'right']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'single')
                    border.set(qn('w:sz'), '4')
                    border.set(qn('w:space'), '4')
                    border.set(qn('w:color'), '000000')
                    p_bdr.append(border)

                p_pr.append(p_bdr)
                new_paragraphs.append(new_paragraph)
            # Добавляем новые параграфы после последнего старого параграфа
            if old_paragraphs:
                insert_position = old_paragraphs[-1]._element
                parent_element = insert_position.getparent()
                insert_index = parent_element.index(insert_position) + 1
                for new_pr in new_paragraphs:
                    parent_element.insert(insert_index, new_pr._element)
                    insert_index += 1
                            
            for paragraph in old_paragraphs:
                if paragraph._p is not None:
                    paragraph._p.getparent().remove(paragraph._p)
                    
                    
            element.docx_listing_paragraphs = new_paragraphs
            element.docx_caption_paragraph.text = element.caption
    
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
            elif hasattr(after, 'formula') and after.docx_table:
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
                    element.docx_table.rows[i].cells[j].text = cell
        elif isinstance(element, Formula):
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            # Create table with 1 row and 3 columns
            table = self.doc.add_table(rows=1, cols=3)

            # Remove borders if you don't want them
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        para.paragraph_format.space_after = 0
                        para.paragraph_format.space_before = 0

            # Column 2 (index 1) - formula centered
            formula_cell = table.cell(0, 1)
            formula_para = formula_cell.paragraphs[0]
            formula_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            formula_run = formula_para.add_run()
            formula_run._element.append(self.formula_meneger._create_omath_element(element.formula))

            # Column 3 (index 2) - caption right-aligned
            caption_cell = table.cell(0, 2)
            caption_para = caption_cell.paragraphs[0]
            caption_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            caption_para.text=(f"{element.caption}")

            # Save table reference if needed
            element.docx_element = table
            element.docx_caption_paragraph=caption_para

            
            
        elif isinstance(element, Listing):
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
        
            element.docx_listing_paragraphs = [self.doc.add_paragraph(line) for line in element.text.split('\n')]
            element.docx_caption_paragraph = self.doc.add_paragraph(element.caption)
            p_bdr = OxmlElement('w:pBdr')  # Создаем элемент границ
            
            for paragraph in element.docx_listing_paragraphs :
                p_pr = paragraph._element.get_or_add_pPr()
                p_bdr = OxmlElement('w:pBdr')

                for border_name in ['top', 'left', 'bottom', 'right']:
                    border = OxmlElement(f'w:{border_name}')
                    border.set(qn('w:val'), 'single')  # Тип линии
                    border.set(qn('w:sz'), '4')         # Толщина (0.5 pt)
                    border.set(qn('w:space'), '4')      # Отступ от текста
                    border.set(qn('w:color'), '000000') # Цвет (#000000)
                    p_bdr.append(border)

            p_pr.append(p_bdr)
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
        # elif isinstance(element, Table):
        #     self.style_manager.apply_table_style(element)
        # elif isinstance(element, Formula):
        #     self.style_manager.apply_formula_style(element)
        # elif isinstance(element, Listing):
        #     self.style_manager.apply_listing_style(element)
        elif isinstance(element, Paragraph):
            self.style_manager.apply_paragraph_style(element)
        elif isinstance(element, ListElement):
            self.style_manager.apply_list_style(element)

 
    def _create_omath_element(self, formula: str):
        """
        Creates an oMath element for a mathematical formula.
        Supports basic mathematical expressions, fractions, exponents, etc.
        
        Args:
            formula: A string representing the mathematical formula (e.g., "E=mc^2")
            
        Returns:
            An OMath XML element ready for insertion into a Word document.
        """
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        def create_run(text):
            """Helper to create a text run with math formatting."""
            r = OxmlElement('m:r')
            t = OxmlElement('m:t')
            t.text = text
            r.append(t)
            return r
        
        def create_frac(num, denom):
            """Creates a fraction element."""
            frac = OxmlElement('m:f')
            
            num_elem = OxmlElement('m:num')
            num_elem.append(create_run(num))
            frac.append(num_elem)
            
            denom_elem = OxmlElement('m:den')
            denom_elem.append(create_run(denom))
            frac.append(denom_elem)
            
            return frac
        
        def create_superscript(base, sup):
            """Creates a superscript element."""
            ssup = OxmlElement('m:sSup')
            
            e = OxmlElement('m:e')
            e.append(create_run(base))
            ssup.append(e)
            
            sup_elem = OxmlElement('m:sup')
            sup_elem.append(create_run(sup))
            ssup.append(sup_elem)
            
            return ssup
        
        def create_subscript(base, sub):
            """Creates a subscript element."""
            ssub = OxmlElement('m:sSub')
            
            e = OxmlElement('m:e')
            e.append(create_run(base))
            ssub.append(e)
            
            sub_elem = OxmlElement('m:sub')
            sub_elem.append(create_run(sub))
            ssub.append(sub_elem)
            
            return ssub
        
        # Create the root oMath element
        omath = OxmlElement('m:oMath')
        
        # Simple parser for basic formulas
        # This is a very basic implementation - consider using a proper parser
        # for complex formulas
        
        # Handle fractions (a/b)
        if '/' in formula:
            num, denom = formula.split('/', 1)
            omath.append(create_frac(num.strip(), denom.strip()))
        # Handle exponents (a^b)
        elif '^' in formula:
            base, exp = formula.split('^', 1)
            omath.append(create_superscript(base.strip(), exp.strip()))
        # Handle subscripts (a_b)
        elif '_' in formula:
            base, sub = formula.split('_', 1)
            omath.append(create_subscript(base.strip(), sub.strip()))
        else:
            # Default case - simple formula
            omath.append(create_run(formula))
        
        return omath
    def load_document(self, doc_path: str):
        """Загружает документ и инициализирует дерево."""
        from maind import parse_document
        self.tree = parse_document(doc_path)
        self.numberer = TreeNumbering(self.tree)
        self.numberer.assign_numbers()
        self.doc = Document(doc_path)
        self.doc_path = doc_path

    def save_document(self, path: Optional[str] = None):
        """Сохраняет документ."""
        self.doc.save(path or self.doc_path)
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
            
            

# Пример использования
if __name__ == "__main__":
    from io import BytesIO
    from PIL import Image as PILImage
    doc_manager = WordDocumentManager("tst.docx")
    doc_manager.load_document("tst.docx")

    # Добавление нового заголовка
    new_header = Header(level=1, text="Новый заголовок", children=[])
    doc_manager.add_element(None, new_header)

    # Создаем тестовое изображение
    img = PILImage.new('RGB', (100, 100), color='gray')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()

    # Добавление изображения под заголовок
    new_image = Image(image_data=image_data, caption="Новое изображение")
    new_imagdasde = Paragraph('dasdasd',None)
    new_imagdasdedsa = Paragraph('dasda32132131231sd',None)
    
    doc_manager.add_element(new_header, new_image)
    doc_manager.add_element(new_image, new_imagdasde)
    doc_manager.add_element(new_image, new_imagdasdedsa)
    new_header2 = Header(level=2, text="Новый222 заголовок", children=[])
    doc_manager.add_element(new_header, new_header2)
    new_imagdasdedsdsa = Paragraph('2020220',None)
    new_imagdasdedsdsa32 = Paragraph('2020220323232',None)
    doc_manager.add_element(new_header2, new_imagdasdedsdsa)
    doc_manager.add_element(new_imagdasdedsdsa, new_imagdasdedsdsa32)
    new_image1 = Image(image_data=image_data, caption="Новdsdasdое изображение")
    doc_manager.add_element(new_header, new_image1)
    
    new_header3 = Header(level=2, text="d заголовок", children=[])
    
    doc_manager.add_element(new_header, new_header3)
    doc_manager.add_element(new_header3,Formula('a-2=2','(dsad'))
    new_imagdasdedsds321a = Paragraph('321321321',None)
    doc_manager.add_element(new_header3, new_imagdasdedsds321a)
    new_header4 = Header(level=3, text="хитрый кейс3333 заголовок", children=[])
    doc_manager.add_element(new_header2,new_header4)
    new_imagdasdeddassds321a = Paragraph('[bnh эомент]',None)
    doc_manager.add_element(new_header4,new_imagdasdeddassds321a)

    new_header5 = Header(level=2, text="Ну если и это заголоовк мошны йто просто молчу", children=[])
    doc_manager.add_element(new_header,new_header5,new_header2)
    
    new_imagdasdedsds321adass = Paragraph('pusin',None)
    new_imagdasdedsds321adass1 = Paragraph('pusin2',None)
    new_imagdasdedsds321adass2 = Paragraph('pusin3',None)
    doc_manager.add_element(new_header5,new_imagdasdedsds321adass)
    doc_manager.add_element(new_imagdasdedsds321adass,new_imagdasdedsds321adass1)
    doc_manager.add_element(new_imagdasdedsds321adass,new_imagdasdedsds321adass2)


    new_header7 = Header(level=1, text="иди сюда заголовок", children=[])
    doc_manager.add_element(None, new_header7)
    new_header8 = Header(level=2, text="иди сюда заголовок 2", children=[])
    doc_manager.add_element(new_header7,new_header8)
    new_imagdasdedsds321adass2ds = Paragraph('susapusin3',None)
    doc_manager.add_element(new_header8,new_imagdasdedsds321adass2ds)

    new_header6 = Header(level=1, text="зайде укак я сюайд", children=[])
    doc_manager.add_element(None,new_header6,new_header)

    new_image3d21 = Image(image_data=image_data, caption="Новое изображение")
    new_image3d21dd = Image(image_data=image_data, caption="Новое 333изображение")

    doc_manager.add_element(new_imagdasdedsds321adass2ds,new_image3d21)
    new_header10 = Header(level=1, text="fasafasfafaf укак я сюайд", children=[])
    doc_manager.add_element(None,new_header10,new_header6)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,new_image3d21dd)
    lit= Listing("code dskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmad","descriptio of code")    
    tab23 = Table([["1","21","3"],["4","5","6"]],'описани таблицы офо')
    tab23e = Table([["1","32321","3"],["4","3213","6"]],'3213описани таблицы офо')
    tab23dase = Formula("E=mc^2","dasdas dsa21",None)
    tab2вы3dase = Formula("E=2332mc^2","d32321asdas dsa21",None)
    tab2вы3dasde = Formula("E=233d2mc^2","d32321asdas dsa21",None)
    
    doc_manager.add_element(new_imagdasdedsds321adass2ds,lit)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23e)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23dase)
    doc_manager.add_element(new_image3d21dd,tab2вы3dase)
    doc_manager.add_element(new_image3d21,tab2вы3dasde)
    test_para = Paragraph('after table?',None)
    lit2= Listing("code dadkmaskdm dsamk dksamkdasmdksajdaskdjnashdbasd jasnjdnasjkdnasjdnasdnasjkdnsadjasn jdsn adjasdnsaj ndjsak","doksddescriptio of code")    
    lit3= Listing("logc32131312ode dadkmaskdm dsamk dksamkdasmdksajdaskdjnashdbasd jasnjdnasjkdnasjdnasdnasjkdnsadjasn jdsn adjasdnsaj ndjsak","doksddescriptio of code")    
    
    doc_manager.add_element(lit,test_para)
    doc_manager.add_element(tab23e,lit2)
    doc_manager.add_element(new_header7,lit3)
    dod_lits = ListElement(['dal 1;',"dal 2;","dal 3."],'–')
    doc_manager.add_element(test_para,dod_lits)
    dkjsad2 = Paragraph('afet s2susapusin3',None)
    doc_manager.add_element(dod_lits,dkjsad2)
    img1 = PILImage.new('RGB', (100, 100), color='red')
    img_byte_arr1 = BytesIO()
    img1.save(img_byte_arr1, format='PNG')
    image_data1 = img_byte_arr1.getvalue()
    lodsds= ListElement(['первый;','второй;', "третий."],'–')
    
    # # Удаление изображения
    doc_manager.remove_element(new_header6)
    doc_manager.remove_element(lit2)
    doc_manager.remove_element(tab23dase)
    doc_manager.remove_element(dod_lits)
    doc_manager.remove_element(new_image3d21dd)
    doc_manager.remove_element(tab23e)
    doc_manager.add_element(lit3,lodsds)
    doc_manager.update_element(new_header10, Header(1,'проверка го гого'))
    doc_manager.add_element(new_header10,Paragraph(" ndskm"))
    doc_manager.update_element(new_header4, Header(1,'ну я хитрееее тебя 333проверка го гого'))
    doc_manager.update_element(dkjsad2, Paragraph("но вот и все par updated"))
    doc_manager.update_element(lodsds, ListElement(['как-то так;','пися231.'],'–'))
    doc_manager.update_element(lodsds, ListElement(['dsadasd;','как-то так;','пися231;','ага.'],'–'))
    doc_manager.update_element (new_image3d21, Image(image_data=image_data1, caption="red one Новое изображение"))
    doc_manager.update_element (tab23, Table([["1","1"],["2","2"],["3","3"]],"Fracation table"))
    ds32 = Table([["01","1"],["02","2"],["3","3"]]," n ni niFracation table")
    doc_manager.add_element(new_header8,ds32)
    doc_manager.update_element (ds32, Table([["10","10"],["20","20"]],"Fracat32ion table"))
    doc_manager.update_element(tab2вы3dase,Formula(r"\frac{1}{2}-\frac{\frac{10}{20}-}{}=30\begin{bmatrix} 1& 1 &1 1 \\ 1& 1 &1 1 \\ 1& 1 &1 1 \end{bmatrix}",''))
    doc_manager.update_element(lit3,Listing(f"poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas",'capton new one'))
    doc_manager.update_element(lit,Listing(f"3213123 1321poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnasposo smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas",'32capton new one'))
    # doc_manager.remove_element(tab2вы3dasde)
    new_header103 = Header(level=3, text="toooto", children=[])

    doc_manager.add_element(new_header8,new_header103)
    doc_manager.add_element(new_header103,Paragraph("32131312412 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header103,Paragraph("dlasjd dk askdj lkasdно вот и все par updated"))
    new_header104 = Header(level=3, text="che dks", children=[])

    doc_manager.add_element(new_header8,new_header104,new_header103)
    doc_manager.add_element(new_header104,Paragraph("IMage knodskd skds;kdaskdkasd 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header104,Paragraph("dasindm; j1nj2eeio12e2m21eio dk askdj lkasdно вот и все par updated dasdasdd ajsdn jasdnjasndj ansdjasn dasnddddddddddddddddddddddddddddddddddsnj ndjs ndj sndj asndjsj"))
    new_header105 = Header(level=3, text="new_header105 che dks", children=[])

    doc_manager.add_element(new_header8,new_header105,new_header103)
    doc_manager.add_element(new_header105,Paragraph("new_header105 knodskd skds;kdaskdkasd 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header105,Paragraph("new_header105; j1nj2eeio12e2m21eio dk askdj lkasdно вот и все par updated"))

    doc_manager.move_element_word(new_header4,new_header8)
    doc_manager.move_element_word(new_header,new_header8,new_header5)
    # doc_manager.move_element_word(None,new_header8,new_header7)
    
    # doc_manager.move_element_word(None, new_header8,new_header7)
    # doc_manager.move_element_word(None, new_header8)
    doc_manager.move_element_word(new_imagdasdedsds321a,new_imagdasdedsds321adass)
    doc_manager.move_element_word(new_imagdasdedsds321a,new_image3d21)
    print_tree(doc_manager.tree)
    doc_manager.save_document()