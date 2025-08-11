
from typing import List
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from config_service import ConfigService
from elements import  Element, Header, Image, Table, Formula, Listing, Paragraph, ListElement
from neighbor_finder import NeighborFinder
from docx import Document
from docx.shared import Pt, Inches

NeighborFinder
class StyleManager:
    def __init__(self, doc: Document,tree: List[Element],):
        self.tree = tree
        self.config_service = ConfigService("formatting_rules.json")
        self.neighbor_finder=NeighborFinder(self.tree)
        self.doc = doc
        self._ensure_styles()

    def _ensure_styles(self):
        """Ensures required styles exist in the document."""
        styles = self.doc.styles
        # style_definitions = [
        #     ("Caption", WD_STYLE_TYPE.PARAGRAPH, "Caption", {"font_size": 9, "italic": True}),
        #     ("Listing", WD_STYLE_TYPE.PARAGRAPH, "Normal", {"font_name": "Courier New", "font_size": 10}),
        #     ("List Bullet", WD_STYLE_TYPE.PARAGRAPH, None, {}),  # Standard unordered list style
        #     ("List Number", WD_STYLE_TYPE.PARAGRAPH, None, {}),  # Standard ordered list style
        # ]

        # for style_name, style_type, base_style, properties in style_definitions:
        #     if style_name not in styles:
        #         style = styles.add_style(style_name, style_type)
        #         if base_style and base_style in styles:
        #             style.base_style = styles[base_style]
        #         for prop, value in properties.items():
        #             if prop == "font_size":
        #                 style.font.size = int(value * 12700)  # Convert points to EMU (1 pt = 12700 EMU)
        #             elif prop == "font_name":
        #                 style.font.name = value
        #             elif prop == "italic":
        #                 style.font.italic = value

    def apply_header_style(self, header:Element):
        if isinstance(header,Header) and header.docx_element:
            # header.docx_element.style = f"Heading {header.level}"
            # run= header.docx_element.runs[0]
            # header.docx_element.clear()
            # run.bold=self.config_service.get("documentFormatting.headings.section.style.bold")
            # paragraph_format = header.docx_element.paragraph_format
            # paragraph_format.space_before = None
            # paragraph_format.space_after = None
            # paragraph_format.left_indent = None
            # paragraph_format.right_indent = None
            # paragraph_format.space_before = Pt(12)  # Интервал перед
            # paragraph_format.space_after = Pt(12)   # Интервал после
            # paragraph_format.line_spacing = 1.5      # Междустрочный интервал
            # # for run in header.docx_element.runs:
            # #     run.clear()
            # # header.docx_element.add_run(header.docx_element.text)
            # # for run in header.docx_element.runs:
            # #     run.font.name ='Arial' # Шрифт
            # #     run.font.size = Pt(14)   # Размер
            # #     run.font.bold = True 
            # custom_style_name = f'MyHeaderStyle'
            # if custom_style_name not in self.doc.styles:
            #     style = self.doc.styles.add_style(custom_style_name, 1)  # 1 = WD_STYLE_TYPE.PARAGRAPH
            #     style.base_style = self.doc.styles[f'Heading {header.level}']
            #     style.font.name = 'Arial'
            #     style.font.size = Pt(14)
            #     style.font.bold = True
            #     style.paragraph_format.space_before = Pt(12)
            #     style.paragraph_format.space_after = Pt(12)

            # # header.docx_element._element.get_or_add_pPr().clear()  # Очистка свойств параграфа
            # # for run in header.docx_element.runs:
            # #     run._element.get_or_add_rPr().clear() # Очистка свойств текста

            # header.docx_element.style = self.doc.styles['MyHeaderStyle']
            # run.font.name=self.config_service.get("documentFormatting.general.font.family")
            # run.font.size=Pt(14)
            # el_before_header=self.neighbor_finder.get_before(header)
            from docx.shared import RGBColor
            run = header.docx_element.runs[0]
            run.font.color.rgb = RGBColor(255, 0, 0)

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