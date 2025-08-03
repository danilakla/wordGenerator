# Класс для нумерации элементов дерева
# Класс для нумерации элементов дерева
from typing import List
from elements import Element, Formula, Header, Image, Listing, Table


class TreeNumbering:
    def __init__(self, tree: List[Element]):
        self.tree = tree
        self.header_counters = [0]  # Стек счетчиков для заголовков (начинается с 0)
        self.element_counters = {
            'Image': 0,
            'Table': 0,
            'Formula': 0,
            'Listing': 0
        }  # Счетчики для каждого типа элемента
        self.current_top_level = "0"  # Номер текущего заголовка верхнего уровня
        self.section_states = {}  # {top_level_number: {'Image': count, 'Table': count, ...}}

    def assign_numbers(self):
        """Инициирует нумерацию всех элементов в дереве."""
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
        """Рекурсивно обходит дерево и присваивает номера."""
        for element in elements:
            if isinstance(element, Header):
                # Обработка заголовка
                if element.level == 1:
                    # Новый заголовок первого уровня: сброс счетчиков
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
                    # Вложенный заголовок: корректировка стека
                    while len(self.header_counters) < element.level:
                        self.header_counters.append(0)
                    while len(self.header_counters) > element.level:
                        self.header_counters.pop()
                    self.header_counters[element.level - 1] = self.header_counters[element.level - 1] + 1 if element.level <= len(self.header_counters) else 1
                # Формируем номер заголовка
                element.text_number_of_element = ".".join(map(str, self.header_counters[:element.level]))
                # Рекурсия для дочерних элементов
                self._number_tree(element.children)
            elif isinstance(element, (Image, Table, Formula, Listing)):
                # Обработка элементов с нумерацией
                element_type = element.__class__.__name__
                self.element_counters[element_type] += 1
                self.section_states[self.current_top_level][element_type] = self.element_counters[element_type]
                element.text_number_of_element = f"{self.current_top_level}.{self.element_counters[element_type]}"
            # Другие элементы (Paragraph, ListElement, UndefinedElement) не нумеруются

    def update_numbering(self, subtree: List[Element], top_level_number: str = None):
        """Обновляет нумерацию для поддерева, начиная с указанного верхнего уровня."""
        if top_level_number is None:
            top_level_number = self.current_top_level
        # Восстанавливаем счетчики для указанного раздела
        self.element_counters = self.section_states.get(top_level_number, {
            'Image': 0,
            'Table': 0,
            'Formula': 0,
            'Listing': 0
        }).copy()
        self.current_top_level = top_level_number
        self._number_tree(subtree)

    def add_element(self, parent: List[Element], element: Element, top_level_number: str):
        """Добавляет новый элемент в дерево и обновляет нумерацию."""
        parent.append(element)
        if isinstance(element, (Image, Table, Formula, Listing)):
            element_type = element.__class__.__name__
            self.element_counters[element_type] = self.section_states.get(top_level_number, {
                'Image': 0,
                'Table': 0,
                'Formula': 0,
                'Listing': 0
            })[element_type] + 1
            element.text_number_of_element = f"{top_level_number}.{self.element_counters[element_type]}"
            self.section_states.setdefault(top_level_number, {
                'Image': 0,
                'Table': 0,
                'Formula': 0,
                'Listing': 0
            })[element_type] = self.element_counters[element_type]
        elif isinstance(element, Header):
            self.update_numbering([element], top_level_number)