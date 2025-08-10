
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.enum.style import WD_STYLE_TYPE
from elements import  Header, Image, Table, Formula, Listing, Paragraph, ListElement

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