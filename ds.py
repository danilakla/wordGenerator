from docx import Document
from lxml import etree
from zipfile import ZipFile
from docx.oxml.ns import qn, nsmap

NAMESPACE = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

def load_numbering_mapping(docx_path):
    """Parse numbering.xml to build a mapping of numId → (format, start, text)."""
    mapping = {}
    with ZipFile(docx_path) as docx:
        if "word/numbering.xml" not in docx.namelist():
            return mapping
        xml_content = docx.read("word/numbering.xml")
        root = etree.fromstring(xml_content)

        # Map abstractNumId → format info
        abstract_nums = {}
        for abs_num in root.findall('w:abstractNum', NAMESPACE):
            abs_num_id = abs_num.get(f'{{{NAMESPACE["w"]}}}abstractNumId')
            lvl_info = {}
            for lvl in abs_num.findall('w:lvl', NAMESPACE):
                ilvl = lvl.get(f'{{{NAMESPACE["w"]}}}ilvl')
                num_format_el = lvl.find('w:numFmt', NAMESPACE)
                lvl_text_el = lvl.find('w:lvlText', NAMESPACE)
                num_format = num_format_el.get(f'{{{NAMESPACE["w"]}}}val') if num_format_el is not None else None
                lvl_text = lvl_text_el.get(f'{{{NAMESPACE["w"]}}}val') if lvl_text_el is not None else None
                lvl_info[int(ilvl)] = (num_format, lvl_text)
            abstract_nums[abs_num_id] = lvl_info

        # Map numId → abstractNumId
        for num in root.findall('w:num', NAMESPACE):
            num_id = num.get(f'{{{NAMESPACE["w"]}}}numId')
            abs_num_id_el = num.find('w:abstractNumId', NAMESPACE)
            abs_num_id = abs_num_id_el.get(f'{{{NAMESPACE["w"]}}}val') if abs_num_id_el is not None else None
            if abs_num_id in abstract_nums:
                mapping[int(num_id)] = abstract_nums[abs_num_id]

    return mapping

def get_paragraph_marker(paragraph, numbering_map):
    """Get the visible bullet/number marker for a paragraph."""
    numPr = paragraph._element.xpath("./w:pPr/w:numPr", nsmap)
    if not numPr:
        return None

    ilvl_el = numPr[0].xpath("./w:ilvl", namespaces=NAMESPACE)
    ilvl = int(ilvl_el[0].get(f'{{{NAMESPACE["w"]}}}val')) if ilvl_el else 0

    numId_el = numPr[0].xpath("./w:numId", namespaces=NAMESPACE)
    numId = int(numId_el[0].get(f'{{{NAMESPACE["w"]}}}val')) if numId_el else 0

    if numId not in numbering_map:
        return None

    lvl_info = numbering_map[numId].get(ilvl, (None, None))
    num_format, lvl_text = lvl_info

    # Determine marker
    if num_format in ("bullet", None):
        return "•"  # Default bullet symbol
    elif num_format == "decimal":
        return lvl_text.replace("%1", "1") if lvl_text else "1."
    elif num_format == "lowerLetter":
        return lvl_text.replace("%1", "a") if lvl_text else "a)"
    elif num_format == "upperLetter":
        return lvl_text.replace("%1", "A") if lvl_text else "A)"
    elif num_format == "lowerRoman":
        return lvl_text.replace("%1", "i") if lvl_text else "i."
    elif num_format == "upperRoman":
        return lvl_text.replace("%1", "I") if lvl_text else "I."
    else:
        return "?."

if __name__ == "__main__":
    docx_path = "example.docx"
    numbering_map = load_numbering_mapping(docx_path)
    doc = Document(docx_path)

    for p in doc.paragraphs:
        marker = get_paragraph_marker(p, numbering_map)
        if marker:
            print(f"{marker} {p.text}")
