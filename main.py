from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Union
from docx import Document
import docx
from docx.document import Document as _Document
from docx.table import Table as _Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

# --- 1) Определяем базовый и конкретные элементы ---

class Element:
    """Базовый класс — для типовой обработки."""
    pass

@dataclass
class Header(Element):
    text: str
    level: int
    paragraph: 'docx.text.paragraph.Paragraph'

@dataclass
class Paragraph(Element):
    text: str
    paragraph: 'docx.text.paragraph.Paragraph'

@dataclass
class ListElement(Element):
    items: List[str]
    paras: List['docx.text.paragraph.Paragraph']
    list_type: str  # 'bullet' или 'numbered'

@dataclass
class Picture(Element):
    image_bytes: bytes
    caption: str
    picture_shape: 'docx.shape.InlineShape'
    caption_para: Optional['docx.text.paragraph.Paragraph']

@dataclass
class TableElement(Element):
    data: List[List[str]]
    caption: str
    table: _Table
    caption_para: Optional['docx.text.paragraph.Paragraph']

@dataclass
class Formula(Element):
    formula: str
    number: str
    para: 'docx.text.paragraph.Paragraph'
    caption_para: Optional['docx.text.paragraph.Paragraph']

@dataclass
class Listing(Element):
    code: str
    caption: str
    para: 'docx.text.paragraph.Paragraph'
    caption_para: Optional['docx.text.paragraph.Paragraph']

# --- 2) Регистрация обработчиков ---

Handler = Callable[[Union['docx.text.paragraph.Paragraph', _Table], Document], Optional[Element]]
_handlers: Dict[str, Handler] = {}

def register_handler(name: str):
    def deco(fn: Handler):
        _handlers[name] = fn
        return fn
    return deco

# --- 3) Утилита: итерация по блокам документа ---

def iter_block_items(parent):
    """
    Генератор, отдающий в порядке документа обёрнутые Paragraph и Table.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    else:
        # для вложенных контейнеров (если нужно) можно взять parent._tc
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield docx.text.paragraph.Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield _Table(child, parent)

# --- 4) Хендлеры для каждого типа ---

@register_handler('header')
def parse_header(block, doc):
    if not hasattr(block, 'style'):
        return None
    style = block.style.name.lower()
    if style.startswith('heading'):
        lvl = int(style.replace('heading', '').strip())
        return Header(text=block.text.strip(),
                      level=lvl,
                      paragraph=block)
    return None

@register_handler('list')
def parse_list(block, doc):
    p = block
    # есть ли у параграфа номерация?
    numPr = getattr(p._p.pPr, 'numPr', None)
    if numPr is None:
        return None
    # уникальный id списка
    numId = numPr.numId.val
    # найдём все подряд идущие с тем же numId
    paras = []
    for q in doc.paragraphs[doc.paragraphs.index(p):]:
        np = getattr(q._p.pPr, 'numPr', None)
        if np and np.numId.val == numId:
            paras.append(q)
        else:
            break
    items = [q.text.strip() for q in paras]
    # определяем тип
    ilvl = paras[0]._p.pPr.numPr.ilvl.val
    list_type = 'numbered' if numPr.numId.val is not None else 'bullet'
    return ListElement(items=items,
                       paras=paras,
                       list_type=list_type)

@register_handler('picture')
def parse_picture(block, doc):
    # ищем inline_shape, связанный с этим параграфом
    for shp in doc.inline_shapes:
        # shp._inline — xml-элемент
        parent_p = shp._inline.getparent()
        # спускаемся до <w:p>
        while parent_p is not None and parent_p.tag.rsplit('}',1)[-1] != 'p':
            parent_p = parent_p.getparent()
        if parent_p is block._p:
            # нашли рисунок, достаём bytes
            rId = shp._inline.graphic.graphicData.pic.blipFill.blip.embed
            image_part = doc.part.related_parts[rId]
            # подпись — следующий параграф, начинающийся с "Рисунок"
            cap_para = None
            idx = doc.paragraphs.index(block) + 1
            if idx < len(doc.paragraphs) and doc.paragraphs[idx].text.startswith('Рисунок'):
                cap_para = doc.paragraphs[idx]
            caption = cap_para.text if cap_para else ''
            return Picture(image_bytes=image_part.blob,
                           caption=caption,
                           picture_shape=shp,
                           caption_para=cap_para)
    return None

@register_handler('table')
def parse_table(block, doc):
    if not isinstance(block, _Table):
        return None
    tbl = block
    # читаем данные
    data = [[cell.text for cell in row.cells] for row in tbl.rows]
    # ищем подпись в ПРЕДЫДУЩЕМ параграфе
    body = doc.element.body
    children = list(body)
    # найти индекс этого <w:tbl>
    idx = children.index(tbl._tbl)
    cap_para = None
    # считаем, сколько ранее было параграфов
    para_count = sum(1 for ch in children[:idx] if ch.tag.rsplit('}',1)[-1]=='p')
    if para_count>0:
        prev_p = doc.paragraphs[para_count-1]
        if prev_p.text.startswith('Таблица'):
            cap_para = prev_p
    caption = cap_para.text if cap_para else ''
    return TableElement(data=data,
                        caption=caption,
                        table=tbl,
                        caption_para=cap_para)

@register_handler('formula')
def parse_formula(block, doc):
    p = block
    txt = p.text.strip()
    # ищем "(X.Y) формула..."
    if txt.startswith('(') and ')' in txt:
        num, rest = txt[1:].split(')',1)
        formula = rest.strip()
        # подпись — следующий параграф, начинающийся с того же номера
        cap_para = None
        idx = doc.paragraphs.index(p)+1
        if idx<len(doc.paragraphs) and doc.paragraphs[idx].text.startswith(f'({num})'):
            cap_para = doc.paragraphs[idx]
        return Formula(formula=formula,
                       number=num,
                       para=p,
                       caption_para=cap_para)
    return None

@register_handler('listing')
def parse_listing(block, doc):
    p = block
    # считаем, что стиль 'Code' или 'Monospaced'
    if p.style.name.lower() in ('code','monospaced'):
        code = p.text
        cap_para = None
        idx = doc.paragraphs.index(p)+1
        if idx<len(doc.paragraphs) and doc.paragraphs[idx].text.lower().startswith('листинг'):
            cap_para = doc.paragraphs[idx]
        caption = cap_para.text if cap_para else ''
        return Listing(code=code,
                       caption=caption,
                       para=p,
                       caption_para=cap_para)
    return None

@register_handler('paragraph')
def parse_paragraph(block, doc):
    # в самом конце — если ничего не подошло выше
    if hasattr(block, 'text') and block.text.strip():
        # исключаем уже распознанные
        return Paragraph(text=block.text.strip(),
                         paragraph=block)
    return None

# --- 5) Парсер документа ---

class DocParser:
    def __init__(self, path: str):
        self.doc = Document(path)
        self.elements: List[Element] = []

    def parse(self) -> List[Element]:
        used = set()  # для списка, чтобы не дублировать
        for block in iter_block_items(self.doc):
            # если уже часть континуальной группы list — пропускаем
            if isinstance(block, type(self.doc.paragraphs[0])):
                # для простоты: skip, если он внутри ListElement уже взят
                if any(isinstance(el, ListElement) and block in el.paras
                       for el in self.elements):
                    continue
            for handler in _handlers.values():
                try:
                    elem = handler(block, self.doc)
                except Exception:
                    elem = None
                if elem:
                    self.elements.append(elem)
                    break
        return self.elements

# --- 6) Как расширять ещё? ---
# 1) Добавляете новый @dataclass(…) с полями, которые вам нужны, включая ссылку
#    на оригинальный параграф/таблицу/shape и подпись/номер там, где надо.
# 2) Пишете @register_handler('your_type') функцию, берёте блок и doc,
#    распознаёте по text/style/xml, возвращаете объект вашего dataclass или None.
# Всё! Центральный DocParser сам при старте увидит и вызовет новый хендлер.

# --- 7) Пример использования ---
if __name__ == '__main__':
    parser = DocParser('example.docx')
    elements = parser.parse()
    for el in elements:
        print(el)
