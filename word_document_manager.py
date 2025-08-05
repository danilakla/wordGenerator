from typing import List, Optional
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from elements import Element, Header, Image, Table, Formula, Listing, Paragraph, ListElement
from tree_numbering import TreeNumbering
from io import BytesIO

class StyleManager:
    def __init__(self, doc: Document):
        self.doc = doc
        self._ensure_styles()

    def _ensure_styles(self):
        """Ensures required styles exist in the document."""
        styles = self.doc.styles
        style_definitions = [
            ("Caption", WD_STYLE_TYPE.PARAGRAPH, "Caption", {"font_size": 9, "italic": True}),
            ("Listing", WD_STYLE_TYPE.PARAGRAPH, "Normal", {"font_name": "Courier New", "font_size": 10}),
            ("List Bullet", WD_STYLE_TYPE.PARAGRAPH, None, {}),  # Standard unordered list style
            ("List Number", WD_STYLE_TYPE.PARAGRAPH, None, {}),  # Standard ordered list style
        ]

        for style_name, style_type, base_style, properties in style_definitions:
            if style_name not in styles:
                style = styles.add_style(style_name, style_type)
                if base_style and base_style in styles:
                    style.base_style = styles[base_style]
                for prop, value in properties.items():
                    if prop == "font_size":
                        style.font.size = int(value * 12700)  # Convert points to EMU (1 pt = 12700 EMU)
                    elif prop == "font_name":
                        style.font.name = value
                    elif prop == "italic":
                        style.font.italic = value

    def apply_header_style(self, header: Header):
        if header.docx_element:
            header.docx_element.style = f"Heading {header.level}"

    def apply_image_style(self, image: Image):
        if image.docx_image_paragraph:
            image.docx_image_paragraph.style = "Normal"
        if image.docx_caption_paragraph:
            image.docx_caption_paragraph.style = "Caption"

    def apply_table_style(self, table: Table):
        if table.docx_table:
            table.docx_table.style = "Table Grid"
        if table.docx_caption_paragraph:
            table.docx_caption_paragraph.style = "Caption"

    def apply_formula_style(self, formula: Formula):
        if formula.docx_element:
            formula.docx_element.style = "Normal"
        if formula.docx_caption_paragraph:
            formula.docx_caption_paragraph.style = "Caption"

    def apply_listing_style(self, listing: Listing):
        for para in listing.docx_listing_paragraphs:
            para.style = "Listing"
        if listing.docx_caption_paragraph:
            listing.docx_caption_paragraph.style = "Caption"

    def apply_paragraph_style(self, paragraph: Paragraph):
        if paragraph.docx_element:
            paragraph.docx_element.style = "Normal"

    def apply_list_style(self, list_element: ListElement):
        style_name = "List Bullet" if list_element.list_type == "unordered" else "List Number"
        for para in list_element.docx_elements:
            para.style = style_name

class WordDocumentManager:
    def __init__(self, doc_path: str):
        self.doc = Document(doc_path)
        self.tree = []
        self.numberer = TreeNumbering(self.tree)
        self.style_manager = StyleManager(self.doc)
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

        self.numberer.assign_numbers()
        self._update_caption(element)
        self._sync_element_to_doc(element, parent, after)
        # self._apply_styles(element)

    def remove_element(self, element: Element):
        """Удаляет элемент из дерева и документа."""
        if isinstance(element, Header) and element.children:
            raise ValueError("Нельзя удалить заголовок с дочерними элементами")

        parent_info = self.numberer.find_parent_and_index(self.tree, element)
        if parent_info is None:
            raise ValueError("Элемент не найден в дереве")

        parent_list, index = parent_info
        parent_list.pop(index)
        self._remove_element_from_doc(element)
        self.numberer.assign_numbers()

    def _update_caption(self, element: Element):
        """Обновляет подпись элемента с учетом номера."""
        if isinstance(element, Image):
            element.caption = f"Рисунок {element.text_number_of_element} – {element.caption or 'Описание'}"
        elif isinstance(element, Table):
            element.caption = f"Таблица {element.text_number_of_element} – {element.caption or 'Описание'}"
        elif isinstance(element, Listing):
            element.caption = f"Листинг {element.text_number_of_element} – {element.caption or 'Описание'}"
        elif isinstance(element, Formula):
            element.caption = f"({element.text_number_of_element})"

    def _sync_element_to_doc(self, element: Element, parent: Optional[Element], after: Optional[Element]):
        """Синхронизирует отдельный элемент с документом."""
        # Определяем позицию вставки
        
        insert_position = None
        if after:
            if hasattr(after, 'docx_element') and after.docx_element:
                insert_position = after.docx_element._element
            elif hasattr(after, 'docx_caption_paragraph') and after.docx_caption_paragraph:
                insert_position = after.docx_caption_paragraph._element
            elif hasattr(after, 'docx_table') and after.docx_table:
                insert_position = after.docx_table._element
        elif parent and isinstance(parent, Header) and parent.docx_element:
            insert_position = parent.docx_element._element
            # Находим последний дочерний элемент, чтобы вставить после него
            for child in parent.children:
                if child == element:
                    break
                if hasattr(child, 'docx_element') and child.docx_element:
                    insert_position = child.docx_element._element
                elif hasattr(child, 'docx_caption_paragraph') and child.docx_caption_paragraph:
                    insert_position = child.docx_caption_paragraph._element
                elif hasattr(child, 'docx_table') and child.docx_table:
                    insert_position = child.docx_table._element

        # Добавляем элемент в документ
        if isinstance(element, Header):
            p = self.doc.add_heading(element.text, level=element.level)
            element.docx_element = p
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
            element.docx_element = self.doc.add_paragraph()
            run = element.docx_element.add_run()
            run._element.append(self._create_omath_element(element.formula))
            run.add_run(f" {element.caption}")
            element.docx_caption_paragraph = element.docx_element
        elif isinstance(element, Listing):
            element.docx_listing_paragraphs = [self.doc.add_paragraph(line) for line in element.text.split('\n')]
            element.docx_caption_paragraph = self.doc.add_paragraph(element.caption)

        # Перемещаем элемент в нужную позицию
        main_element = None
        if hasattr(element, 'docx_element') and element.docx_element:
            main_element = element.docx_element._element
        elif hasattr(element, 'docx_image_paragraph') and element.docx_image_paragraph:
            main_element = element.docx_image_paragraph._element
        elif hasattr(element, 'docx_table') and element.docx_table:
            main_element = element.docx_table._element

        if insert_position is not None and main_element is not None:
            # Вставляем после insert_position
            parent_element = insert_position.getparent()
            insert_index = parent_element.index(insert_position) + 1
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
        elif isinstance(element, Formula) and element.docx_element:
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

    def _create_omath_element(self, formula: str):
        """Создает oMath элемент для формулы (заглушка, требует доработки)."""
        from docx.oxml import OxmlElement
        omath = OxmlElement('m:oMath')
        # Здесь нужно добавить парсинг formula в MathML, если требуется
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

# Пример использования
if __name__ == "__main__":
    from io import BytesIO
    from PIL import Image as PILImage
    doc_manager = WordDocumentManager("example.docx")
    doc_manager.load_document("example.docx")

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
    
    new_header3 = Header(level=2, text="3333 заголовок", children=[])
    doc_manager.add_element(new_header, new_header3)
    new_imagdasdedsds321a = Paragraph('2020220',None)
    doc_manager.add_element(new_header3, new_imagdasdedsds321a)

    # Удаление изображения
    # doc_manager.remove_element(new_image)

    doc_manager.save_document()