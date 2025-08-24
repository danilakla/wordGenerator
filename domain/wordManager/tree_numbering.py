import copy
import re
from typing import List, Optional
from elements.element import Element
from elements.header import Header
from elements.formula import Formula
from elements.image import Image
from elements.list_element import ListElement
from elements.listing import Listing
from elements.table import Table
from elements.paragraph import Paragraph

class TreeNumbering:
    def __init__(self, tree: List[Element]):
        self.tree = tree
        self.header_counters = [0]  # Stack of counters for headers (starts with 0)
        self.element_counters = {
            'Image': 0,
            'Table': 0,
            'Formula': 0,
            'Listing': 0
        }  # Counters for each element type
        self.current_top_level = "0"  # Number of the current top-level header
        self.section_states = {}  # {top_level_number: {'Image': count, 'Table': count, ...}}

    def assign_numbers(self):
        """Initiates numbering of all elements in the tree."""
        self.header_counters = [0]
        self.element_counters = {
            'Image': 0,
            'Table': 0,
            'Formula': 0,
            'Listing': 0
        }
        self.current_top_level = "0"
        self.section_states = {}
        self._number_tree(self.tree)

    def _number_tree(self, elements: List[Element]):
        """Recursively traverses the tree and assigns numbers."""
        for element in elements:
            if isinstance(element, Header):
                # Handle header
                if element.level == 1:
                    # New top-level header: reset counters
                    self.header_counters = [self.header_counters[0] + 1]
                    self.element_counters = {
                        'Image': 0,
                        'Table': 0,
                        'Formula': 0,
                        'Listing': 0
                    }
                    self.current_top_level = str(self.header_counters[0])
                    self.section_states[self.current_top_level] = {
                        'Image': 0,
                        'Table': 0,
                        'Formula': 0,
                        'Listing': 0
                    }
                else:
                    # Nested header: adjust stack
                    while len(self.header_counters) < element.level:
                        self.header_counters.append(0)
                    while len(self.header_counters) > element.level:
                        self.header_counters.pop()
                    self.header_counters[element.level - 1] = self.header_counters[element.level - 1] + 1 if element.level <= len(self.header_counters) else 1
                # Form header number
                element.text_number_of_element = ".".join(map(str, self.header_counters[:element.level]))
                element.text =f"{element.text_number_of_element} {self.extract_text_after_leading_numbers(element.text)}"
                if element.docx_element is not None and element.docx_element.text is not None:
                    for i, run in enumerate(element.docx_element.runs):
                        if i != 0:  # Пропускаем первый элемент (индекс 0)
                            run.clear()
                    if element.docx_element.runs:
                        element.docx_element.runs[0].text=element.text
                    
                   
                # Recursion for child elements
                self._number_tree(element.children)
            elif isinstance(element, (Image, Table, Formula, Listing)):
                # Handle numbered elements
                element_type = element.__class__.__name__
                self.element_counters[element_type] += 1
                self.section_states[self.current_top_level][element_type] = self.element_counters[element_type]
                element.text_number_of_element = f"{self.current_top_level}.{self.element_counters[element_type]}"
                self._update_caption(element)
            # Other elements (Paragraph, ListElement, UndefinedElement) are not numbered
    def extract_text_after_leading_numbers(self,text: str) -> str:
        """
        Извлекает текст, идущий после всех чисел в начале строки.
        Если чисел нет — возвращает исходный текст.

        Примеры:
            - "1.1.1 1.1.1 текст" → "текст"
            - "123.45 цена" → "цена"
            - "200 руб" → "руб"
            - "Цена 100" → "Цена 100" (число не в начале)
            - "Просто текст" → "Просто текст"
        """
        # Удаляем все числа (целые, дробные, с множеством точек) в начале строки
        cleaned_text = re.sub(r"^(\d+[\.\d]*\s*)+", "", text).strip()
        return cleaned_text if cleaned_text else text
    def clean_caption(self,caption: str) -> str:
        """
        Если строка соответствует одному из шаблонов:
        - "Таблица X.X – ..."
        - "Рисунок X.X – ..." 
        - "Листинг X.X – ..."
        возвращает только текст после " – ".
        В противном случае возвращает строку без изменений.
        """
        patterns = [
            r'^Таблица \d+\.\d+ – .+$',
            r'^Рисунок \d+\.\d+ – .+$',
            r'^Листинг \d+\.\d+ – .+$'
        ]

        # Проверяем соответствие хотя бы одному паттерну
        if any(re.match(pattern, caption) for pattern in patterns):
            return caption.split(" – ", 1)[-1].strip()
        return caption
    def _update_caption(self, element: Element):
        """Обновляет подпись элемента с учетом номера."""
        if isinstance(element, Image):
            element.caption = f"Рисунок {element.text_number_of_element} – {self.clean_caption(element.caption) or 'Описание'}"
        elif isinstance(element, Table):
            element.caption = f"Таблица {element.text_number_of_element} – {self.clean_caption(element.caption) or 'Описание'}"
        elif isinstance(element, Listing):
            element.caption = f"Листинг {element.text_number_of_element} – {self.clean_caption(element.caption) or 'Описание'}"
        elif isinstance(element, Formula):
            element.caption = f"({element.text_number_of_element})"
        if element.docx_caption_paragraph is not None and element.docx_caption_paragraph.text is not None:    
            for i, run in enumerate(element.docx_caption_paragraph.runs):
                if i != 0:  # Пропускаем первый элемент (индекс 0)
                    run.clear()
            if element.docx_caption_paragraph.runs:
                element.docx_caption_paragraph.runs[0].text=element.caption
    def update_numbering(self, subtree: List[Element], top_level_number: str = None):
        """Updates numbering for a subtree, starting from the specified top level."""
        if top_level_number is None:
            top_level_number = self.current_top_level
        # Restore counters for the specified section
        self.element_counters = self.section_states.get(top_level_number, {
            'Image': 0,
            'Table': 0,
            'Formula': 0,
            'Listing': 0
        }).copy()
        self.current_top_level = top_level_number
        self._number_tree(subtree)
    def find_parent_element(self,elements: List[Element], target_element: Element) -> Optional[Element]:
        """
        Finds the parent element of the target_element in the given list of elements.
        
        Args:
            elements: List of Element objects to search through.
            target_element: The element whose parent we want to find.
            
        Returns:
            The parent Element if found, None otherwise.
        """
        # Iterate through all elements to find the parent
        for element in elements:
            # Check if the current element is a Header (the only type that can have children)
            if isinstance(element, Header):
                # Check if the target_element is in the children of this Header
                if target_element in element.children:
                    return element
                # Recursively check the children of this Header
                parent = self.find_parent_element(element.children, target_element)
                if parent is not None:
                    return parent
        # If no parent is found, return None
        return None 
    def find_parent_and_index(self, current_list: List[Element], target: Element) -> tuple[List[Element], int] | None:
        """Finds the parent list and index of the target element in the tree."""
        for i, elem in enumerate(current_list):
            if elem == target:
                return current_list, i
            if isinstance(elem, Header):
                result = self.find_parent_and_index(elem.children, target)
                if result is not None:
                    return result
        return None
    def update_element_content(self, element: Element, update_element: Element):
        """
        Updates the content or caption of an element in the tree and triggers renumbering if needed.
        
        Args:
            element: The element to update (Header, Paragraph, ListElement, Image, Table, Formula, Listing).
            new_content: The new content (str for text/caption/formula, List[List[str]] for Table data, List[str] for ListElement items).
            field: The field to update ('content' for text/data/formula/items, 'caption' for caption).
        """
        if isinstance(element, Header):
            element.text=f"{element.text_number_of_element} {update_element.text}"
        elif isinstance(element, Paragraph):
            element.text = update_element.text
        elif isinstance(element, ListElement):
            element.items = list(update_element.items)
        elif isinstance(element, Image):
            element.caption = f"Рисунок {element.text_number_of_element} – {update_element.caption}"
            element.image_data =  update_element.image_data
            
        elif isinstance(element, Table):
            element.caption = f"Таблица {element.text_number_of_element} – {update_element.caption}"
            for i, row in enumerate(element.data):
                for j, cell in enumerate(row):
                    cell.data = update_element.data[i][j].data
                    cell.horizontal = update_element.data[i][j].horizontal
                    cell.vertical = update_element.data[i][j].vertical
        elif isinstance(element, Formula):
            element.formula = update_element.formula
        elif isinstance(element, Listing):
            element.caption = f"Листинг {element.text_number_of_element} – {update_element.caption}"
            element.text =update_element.text 
            
    def add_after(self, existing_element: Element, new_element: Element):
        """Adds a new element after the specified existing element and updates numbering if necessary."""
        if isinstance(existing_element, (Header)):
            self.add_child_to_header(existing_element,new_element)
            return
            
        parent, index = self.find_parent_and_index(self.tree, existing_element)
        if parent is not None:
            parent.insert(index + 1, new_element)
            if isinstance(new_element, (Header, Image, Table, Formula, Listing)):
                self.assign_numbers()
        else:
            raise ValueError("Existing element not found in the tree")
    def add_child_to_header(self, parent_header: Header, new_element: Element):
        """Добавляет новый элемент как дочерний для указанного заголовка и обновляет нумерацию при необходимости."""
        parent_header.children.insert(0,new_element)
        if isinstance(new_element, (Header, Image, Table, Formula, Listing)):
            self.assign_numbers()

    def add_nested_header(self, parent_header: Header, new_header: Header, after_child: Optional[Header] = None):
        """Adds a new header as a child of the specified parent header, after the specified child if provided."""
        if after_child is not None:
            try:
                index = parent_header.children.index(after_child)
                parent_header.children.insert(index + 1, new_header)
            except ValueError:
                raise ValueError("After child not found in parent's children")
        else:
            parent_header.children.append(new_header)
        self.assign_numbers()

    def add_top_level_header(self, new_header: Header, after_header: Optional[Header] = None):
        """Adds a new top-level header after the specified header if provided, otherwise appends to the end."""
        if new_header.level != 1:
            raise ValueError("Top-level header must have level 1")
        if after_header is not None:
            try:
                index = self.tree.index(after_header)
                self.tree.insert(index + 1, new_header)
            except ValueError:
                raise ValueError("After header not found in top-level tree")
        else:
            self.tree.append(new_header)
        self.assign_numbers()
    def adjust_header_levels(self,parent: Header, child: Header):
        if parent  is None:
           child.level=1 
        else:
            new_child_level = parent.level + 1
            child.level = new_child_level

        # Recursively adjust all children of this child
        for element in child.children:
            if isinstance(element, Header):
                # For each grandchild, maintain the same relative level difference
                # but based on the new child level
                self.adjust_header_levels(child, element)
    def move_element(self, parent: Element, element: Element, after:Element=None):

        parent_info = self.find_parent_and_index(self.tree, element)
        if parent_info is None:
            raise ValueError("Элемент не найден в дереве")

        parent_list, index = parent_info
        parent_list.pop(index)
        if isinstance(element, Header):
            if parent is None:

                self.add_top_level_header(element, after_header=after)
            else:
                self.add_nested_header(parent, element, after_child=after)
        else:
            if parent is None:
                raise ValueError("Non-header elements must have a parent")
            self.add_after(parent, element)
            if not isinstance(parent,Header):
                after=parent

        self.assign_numbers()