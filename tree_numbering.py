from typing import List, Optional
from elements import Element, Formula, Header, Image, Listing, Table

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
                # Recursion for child elements
                self._number_tree(element.children)
            elif isinstance(element, (Image, Table, Formula, Listing)):
                # Handle numbered elements
                element_type = element.__class__.__name__
                self.element_counters[element_type] += 1
                self.section_states[self.current_top_level][element_type] = self.element_counters[element_type]
                element.text_number_of_element = f"{self.current_top_level}.{self.element_counters[element_type]}"
            # Other elements (Paragraph, ListElement, UndefinedElement) are not numbered

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
    