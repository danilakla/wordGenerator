from dataclasses import dataclass, field
import re
from typing import List, Optional
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable
from docx.oxml.ns import qn
from docx.oxml.ns import nsmap  # Добавляем импорт nsmap

# Базовый класс для элементов (без полей)
class Element:
    pass

# Заголовок
@dataclass
class Header(Element):
    level: int
    text: str
    children: List['Element'] = field(default_factory=list)
    docx_element: Optional[DocxParagraph] = None

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

# Рисунок
@dataclass
class Image(Element):
    image_data: bytes
    caption: str
    docx_image_paragraph: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None

# Таблица
@dataclass
class Table(Element):
    data: List[List[str]]
    caption: str
    docx_table: Optional[DocxTable] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None

# Формула
@dataclass
class Formula(Element):
    formula: str
    caption: str
    docx_element: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None

# Листинг
@dataclass
class Listing(Element):
    text: str
    caption: str
    docx_listing_paragraph: Optional[DocxParagraph] = None
    docx_caption_paragraph: Optional[DocxParagraph] = None

# Неизвестный элемент
@dataclass
class UndefinedElement(Element):
    content: str
    docx_element: Optional[object] = None

# Вспомогательные функции
def is_header(paragraph):
    return paragraph.style.name.startswith('Heading')

def get_header_level(paragraph):
    return int(paragraph.style.name.split()[1]) if paragraph.style.name.startswith('Heading') else 1

def is_list_item(paragraph):
    return paragraph.style.name in ['List Bullet', 'List Number']

def get_list_type(paragraph):
    return 'unordered' if paragraph.style.name == 'List Bullet' else 'ordered'

def is_table_caption(paragraph):
    text = paragraph.text.strip()
    pattern = r'^Таблица \d+\.\d+ – .+$'
    return bool(re.fullmatch(pattern, text))

def is_image_caption(paragraph):
    text = paragraph.text.strip()
    pattern = r'^Рисунок \d+\.\d+ – .+$'
    return bool(re.fullmatch(pattern, text))

def is_listing_caption(paragraph):
    text = paragraph.text.strip()
    pattern = r'^Листинг \d+\.\d+ – .+$'
    return bool(re.fullmatch(pattern, text))

def has_image(paragraph):
    # Проверяем наличие изображения через runs или inline shapes
    has_pic = any(run.element.tag.endswith('pic') for run in paragraph.runs)
    has_inline = paragraph._element.xpath('.//wp:inline')
    # print(f"Checking paragraph for image: has_pic={has_pic}, has_inline={has_inline}")
    return has_pic or has_inline

def extract_image(paragraph):
    # Удаляем явное определение namespaces, используем nsmap
    for run in paragraph.runs:
        if run.element.tag.endswith('pic'):
            blip = run.element.find('.//a:blip', namespaces=nsmap)  # Используем nsmap
            if blip is not None:
                rId = blip.get(qn('r:embed'))
                if rId and rId in paragraph.part.related_parts:
                    image_part = paragraph.part.related_parts[rId]
                    return image_part.blob

    # Исправляем вызов xpath -> findall с nsmap
    for inline in paragraph._element.findall('.//wp:inline', namespaces=nsmap):
        blip = inline.find('.//a:blip', namespaces=nsmap)
        if blip is not None:
            rId = blip.get(qn('r:embed'))
            if rId and rId in paragraph.part.related_parts:
                image_part = paragraph.part.related_parts[rId]
                return image_part.blob
                
    return b''

def has_formula(paragraph):
    return any(run.element.tag.endswith('oMath') for run in paragraph.runs)

def extract_formula_and_caption(paragraph):
    caption = None
    formula_xml = []
    for run in paragraph.runs:
        text = run.text.strip()
        if text.startswith('(') and text.endswith(')'):
            caption = text
        elif run.element.tag.endswith('oMath'):
            formula_xml.append(run.element.xml)
    formula = ''.join(formula_xml)
    return formula, caption if formula else (None, None)

def is_listing(paragraph):
    return paragraph.style.name == 'Listing'

# Основная функция парсинга
def parse_document(doc_path):
    doc = Document(doc_path)
    tree = []
    stack = [tree]
    current_level = 0
    pending_table_caption = None
    paragraph_index = 0
    table_index = 0
    elements = list(doc.element.body)

    i = 0
    while i < len(elements):
        element = elements[i]
        if element.tag.endswith('p'):
            if paragraph_index >= len(doc.paragraphs):
                parent = stack[-1]
                parent.append(UndefinedElement(str(element), element))
                i += 1
                continue
            paragraph = doc.paragraphs[paragraph_index]
            paragraph_index += 1
            if is_header(paragraph):
                level = get_header_level(paragraph)
                text = paragraph.text
                while len(stack) > 1 and current_level >= level:
                    stack.pop()
                    current_level -= 1
                parent = stack[-1]
                new_header = Header(level, text, [], paragraph)
                parent.append(new_header)
                stack.append(new_header.children)
                current_level = level
                i += 1
            elif is_list_item(paragraph):
                list_type = get_list_type(paragraph)
                list_items = [paragraph.text]
                list_paragraphs = [paragraph]
                j = i + 1
                next_paragraph_index = paragraph_index
                while (j < len(elements) and elements[j].tag.endswith('p') and 
                       next_paragraph_index < len(doc.paragraphs) and
                       is_list_item(doc.paragraphs[next_paragraph_index]) and 
                       get_list_type(doc.paragraphs[next_paragraph_index]) == list_type):
                    list_items.append(doc.paragraphs[next_paragraph_index].text)
                    list_paragraphs.append(doc.paragraphs[next_paragraph_index])
                    next_paragraph_index += 1
                    j += 1
                parent = stack[-1]
                parent.append(ListElement(list_items, list_type, list_paragraphs))
                i = j
                paragraph_index = next_paragraph_index
            elif is_table_caption(paragraph):
                pending_table_caption = (paragraph.text, paragraph)
                i += 1
            elif has_image(paragraph):
                image_data = extract_image(paragraph)
                caption = None
                caption_paragraph = None
                if (i + 1 < len(elements) and elements[i + 1].tag.endswith('p') and 
                    paragraph_index < len(doc.paragraphs) and
                    is_image_caption(doc.paragraphs[paragraph_index])):
                    caption = doc.paragraphs[paragraph_index].text
                    caption_paragraph = doc.paragraphs[paragraph_index]
                    paragraph_index += 1
                    i += 1
                parent = stack[-1]
                parent.append(Image(image_data, caption, paragraph, caption_paragraph))
                i += 1
            elif has_formula(paragraph):
                formula, caption = extract_formula_and_caption(paragraph)
                if formula:
                    parent = stack[-1]
                    parent.append(Formula(formula, caption, paragraph, None))
                i += 1
            elif is_listing(paragraph):
                text = paragraph.text
                caption = None
                caption_paragraph = None
                if (i + 1 < len(elements) and elements[i + 1].tag.endswith('p') and 
                    paragraph_index < len(doc.paragraphs) and
                    is_listing_caption(doc.paragraphs[paragraph_index])):
                    caption = doc.paragraphs[paragraph_index].text
                    caption_paragraph = doc.paragraphs[paragraph_index]
                    paragraph_index += 1
                    i += 1
                parent = stack[-1]
                parent.append(Listing(text, caption, paragraph, caption_paragraph))
                i += 1
            else:
                parent = stack[-1]
                parent.append(Paragraph(paragraph.text, paragraph))
                i += 1
        elif element.tag.endswith('tbl'):
            if table_index < len(doc.tables):
                table = doc.tables[table_index]
                table_index += 1
                caption, caption_paragraph = pending_table_caption if pending_table_caption else (None, None)
                pending_table_caption = None
                data = [[cell.text for cell in row.cells] for row in table.rows]
                parent = stack[-1]
                parent.append(Table(data, caption, table, caption_paragraph))
            else:
                parent = stack[-1]
                parent.append(UndefinedElement(str(element), element))
            i += 1
        else:
            parent = stack[-1]
            parent.append(UndefinedElement(str(element), element))
            i += 1

    return tree

# Функция для красивого вывода дерева
def print_tree(elements, indent=0, prefix=""):
    for i, elem in enumerate(elements):
        is_last = i == len(elements) - 1
        branch = "└── " if is_last else "├── "
        indent_str = prefix + branch
        content = ""
        
        if isinstance(elem, Header):
            content = f"Header (Level {elem.level}): {elem.text[:50]}{'...' if len(elem.text) > 50 else ''}"
        elif isinstance(elem, Paragraph):
            content = f"Paragraph: {elem.text[:50]}{'...' if len(elem.text) > 50 else ''}"
        elif isinstance(elem, ListElement):
            content = f"List ({elem.list_type}): {len(elem.items)} items"
        elif isinstance(elem, Image):
            content = f"Image: {elem.caption[:50] if elem.caption else 'No caption'}{'...' if elem.caption and len(elem.caption) > 50 else ''}"
        elif isinstance(elem, Table):
            content = f"Table: {len(elem.data)} rows, {elem.caption[:50] if elem.caption else 'No caption'}{'...' if elem.caption and len(elem.caption) > 50 else ''}"
        elif isinstance(elem, Formula):
            content = f"Formula: {elem.caption[:50] if elem.caption else 'No caption'}{'...' if elem.caption and len(elem.caption) > 50 else ''}"
        elif isinstance(elem, Listing):
            content = f"Listing: {elem.caption[:50] if elem.caption else 'No caption'}{'...' if elem.caption and len(elem.caption) > 50 else ''}"
        elif isinstance(elem, UndefinedElement):
            content = f"Undefined: {elem.content[:50]}{'...' if len(elem.content) > 50 else ''}"
        
        print(f"{indent_str}{content}")
        
        if isinstance(elem, Header) and elem.children:
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(elem.children, indent + 1, new_prefix)

# Пример использования
if __name__ == "__main__":
    doc_path = "example.docx"
    elements_tree = parse_document(doc_path)
    print("Document Structure:")
    print_tree(elements_tree)