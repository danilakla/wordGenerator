from docx.oxml import parse_xml
from latex2mathml.converter import convert as latex_to_mathml
from lxml import etree

class FormulaHelper:
    def __init__(self, xslt_path="mml2omml.xsl"):
        # Загружаем XSLT-конвертер MathML → OMML
        xslt = etree.parse(xslt_path)
        self.transform = etree.XSLT(xslt)

    def _create_omath_element(self, latex_formula: str):
        """
        Конвертирует LaTeX-формулу в OMML (Office Math) для вставки в Word.
        Поддерживает любые сложные формулы.
        """
        # 1. LaTeX → MathML
        mathml = latex_to_mathml(latex_formula)

        # 2. MathML → OMML
        mathml_tree = etree.fromstring(mathml.encode("utf-8"))
        omml_tree = self.transform(mathml_tree)

        # 3. Преобразуем в XML-элемент python-docx
        omml_element = parse_xml(etree.tostring(omml_tree.getroot()))
        return omml_element
