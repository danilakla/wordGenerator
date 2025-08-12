
from typing import List
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from config_service import ConfigService
from elements import  Element, Header, Image, Table, Formula, Listing, Paragraph, ListElement
from neighbor_finder import NeighborFinder
from docx import Document
from docx.shared import Pt, RGBColor,Inches
from docx.enum.dml import MSO_THEME_COLOR
from docx.enum.text import WD_LINE_SPACING
from docx.enum.text import WD_ALIGN_PARAGRAPH
NeighborFinder
class StyleManager:
    
    def __init__(self, doc: Document,tree: List[Element],):
        self.tree = tree
        self.COLOR_MAP = {
    "black": RGBColor(0, 0, 0),
    "white": RGBColor(255, 255, 255),
    "red": RGBColor(255, 0, 0),
    "green": RGBColor(0, 255, 0),
    "blue": RGBColor(0, 0, 255),
    # Add more as needed
}
        
        self.WD_LINE_SPACING_MAP = {
    "single":WD_LINE_SPACING.SINGLE,
    "Multiple": WD_LINE_SPACING.MULTIPLE,
    "Double": WD_LINE_SPACING.DOUBLE,
    "AtLeast": WD_LINE_SPACING.AT_LEAST,
    "Exactyl": WD_LINE_SPACING.EXACTLY
    # Add more as needed
}
        
        self.WD_ALIGN_PARAGRAPH_MAP = {
    "center":WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY
    # Add more as needed
}
        self.config_service = ConfigService("formatting_rules.json")
        self.neighbor_finder=NeighborFinder(self.tree)
        self.doc = doc
        self._ensure_styles()
        

    def _ensure_styles(self):
        """Ensures required styles exist in the document."""
        styles = self.doc.styles

# Устанавливаем разрыв страницы перед каждым таким заголовком
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
    def cm_to_pt(self,cm):
        """Конвертирует сантиметры в пункты (1 см ≈ 28.35 pt)."""
        return Pt(cm * 28.3464567)
    def apply_header_style(self, header:Header):
        if  header.docx_element:
            for run in header.docx_element.runs:
                run.font.name = self.config_service.get("documentFormatting.headings.font.family")  
                run.font.size = Pt(self.config_service.get("documentFormatting.headings.font.size"))   
                run.font.bold = self.config_service.get("documentFormatting.headings.font.style.bold")       
                run.font.italic = self.config_service.get("documentFormatting.headings.font.style.italic")  
                run.font.color.rgb = self.COLOR_MAP[self.config_service.get("documentFormatting.headings.font.color")] 

            paragraph_format  = header.docx_element.paragraph_format
            paragraph_format.line_spacing_rule  =self.WD_LINE_SPACING_MAP[self.config_service.get("documentFormatting.headings.font.lineSpacing", 0)]
            paragraph_format.left_indent = Pt(self.config_service.get("documentFormatting.headings.section.paragraph_format.indent_left", 0))      
            paragraph_format.right_indent = Pt(self.config_service.get("documentFormatting.headings.section.paragraph_format.indent_right", 0))   
            paragraph_format.first_line_indent = self.cm_to_pt(self.config_service.get("documentFormatting.headings.section.paragraph_format.first_line", 0))
            neighbor_before = self.neighbor_finder.get_before(header)
            if header.level==1:
                paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.headings.section.paragraph_format.spacingBefore", 0))  # Space before paragraph
                paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.headings.section.paragraph_format.spacingAfter", 0))
              
            elif header.level>1:
                if isinstance(neighbor_before,Header):
                    neighbor_before.docx_element.paragraph_format.space_after=Pt(self.config_service.get("documentFormatting.headings.subsection.spacingBeforeAnotherSubSection", 0))  # Space before paragraph
                    paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.headings.subsection.spacingBeforeAnotherSubSection", 0))  # Space before paragraph
                    paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.headings.subsection.spacingAfter", 0))
                else:
                    paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.headings.subsection.spacingBefore", 0))  # Space before paragraph
                    paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.headings.subsection.spacingAfter", 0))

    def apply_image_style(self, image: Image):
        for run in image.docx_caption_paragraph.runs:
            run.font.name = self.config_service.get("documentFormatting.figures.family")  
            run.font.size = Pt(self.config_service.get("documentFormatting.figures.size"))   
            run.font.bold = self.config_service.get("documentFormatting.figures.style.bold")       
            run.font.italic = self.config_service.get("documentFormatting.figures.style.italic")  
            run.font.color.rgb = self.COLOR_MAP[self.config_service.get("documentFormatting.figures.color")] 
        
        paragraph_format  = image.docx_caption_paragraph.paragraph_format
        paragraph_format.line_spacing_rule  =self.WD_LINE_SPACING_MAP[self.config_service.get("documentFormatting.figures.lineSpacing", 0)]
        paragraph_format.left_indent = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.indent_left", 0))      
        paragraph_format.right_indent = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.indent_right", 0))   
        paragraph_format.first_line_indent = self.cm_to_pt(self.config_service.get("documentFormatting.figures.paragraph_format.first_line", 0))
        paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.spacingBefore", 0))  # Space before paragraph
        paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.spacingAfter", 0))
        paragraph_format.alignment=self.WD_ALIGN_PARAGRAPH_MAP[self.config_service.get("documentFormatting.figures.caption.alignment", 0)]

        paragraph_format  = image.docx_image_paragraph.paragraph_format
        paragraph_format.line_spacing_rule  =self.WD_LINE_SPACING_MAP[self.config_service.get("documentFormatting.figures.lineSpacing", 0)]
        paragraph_format.left_indent = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.indent_left", 0))      
        paragraph_format.right_indent = Pt(self.config_service.get("documentFormatting.figures.paragraph_format.indent_right", 0))   
        paragraph_format.first_line_indent = self.cm_to_pt(self.config_service.get("documentFormatting.figures.paragraph_format.first_line", 0))
        paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.figures.spacingBefore", 0))  # Space before paragraph
        paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.figures.spacingAfter", 0))
        paragraph_format.alignment=self.WD_ALIGN_PARAGRAPH_MAP[self.config_service.get("documentFormatting.figures.alignment", 0)]
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
        for run in paragraph.docx_element.runs:
                run.font.name = self.config_service.get("documentFormatting.paragraph.family")  
                run.font.size = Pt(self.config_service.get("documentFormatting.paragraph.size"))   
                run.font.bold = self.config_service.get("documentFormatting.paragraph.style.bold")       
                run.font.italic = self.config_service.get("documentFormatting.paragraph.style.italic")  
                run.font.color.rgb = self.COLOR_MAP[self.config_service.get("documentFormatting.paragraph.color")] 

        paragraph_format  = paragraph.docx_element.paragraph_format
        paragraph_format.line_spacing_rule  =self.WD_LINE_SPACING_MAP[self.config_service.get("documentFormatting.paragraph.lineSpacing", 0)]
        paragraph_format.left_indent = Pt(self.config_service.get("documentFormatting.paragraph.paragraph_format.indent_left", 0))      
        paragraph_format.right_indent = Pt(self.config_service.get("documentFormatting.paragraph.paragraph_format.indent_right", 0))   
        paragraph_format.first_line_indent = self.cm_to_pt(self.config_service.get("documentFormatting.paragraph.paragraph_format.first_line", 0))
        paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.paragraph.paragraph_format.spacingBefore", 0))  # Space before paragraph
        paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.paragraph.paragraph_format.spacingAfter", 0))
          


    def apply_list_style(self, list_element: ListElement):
        for list_item in list_element.docx_elements:
            for run in list_item.runs:
                run.font.name = self.config_service.get("documentFormatting.lists.family")  
                run.font.size = Pt(self.config_service.get("documentFormatting.lists.size"))   
                run.font.bold = self.config_service.get("documentFormatting.lists.style.bold")       
                run.font.italic = self.config_service.get("documentFormatting.lists.style.italic")  
                run.font.color.rgb = self.COLOR_MAP[self.config_service.get("documentFormatting.lists.color")] 

            paragraph_format  = list_item.paragraph_format
            paragraph_format.line_spacing_rule  =self.WD_LINE_SPACING_MAP[self.config_service.get("documentFormatting.lists.lineSpacing", 0)]
            paragraph_format.left_indent = Pt(self.config_service.get("documentFormatting.lists.paragraph_format.indent_left", 0))      
            paragraph_format.right_indent = Pt(self.config_service.get("documentFormatting.lists.paragraph_format.indent_right", 0))   
            paragraph_format.first_line_indent = self.cm_to_pt(self.config_service.get("documentFormatting.lists.paragraph_format.first_line", 0))
            paragraph_format.space_before = Pt(self.config_service.get("documentFormatting.lists.paragraph_format.spacingBefore", 0))  # Space before paragraph
            paragraph_format.space_after = Pt(self.config_service.get("documentFormatting.lists.paragraph_format.spacingAfter", 0))