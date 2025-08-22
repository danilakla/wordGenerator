# Пример использования
import copy
from typing import  List, Optional
from docx import Document
from domain.wordManager.word_document_manager import WordDocumentManager
from elements.element import Element
from elements.header import Header
from elements.formula import Formula
from elements.image import Image
from elements.list_element import ListElement
from elements.listing import Listing
from elements.table import Table, DataTable
from elements.paragraph import Paragraph
from domain.styleManager.style_manager import StyleManager
from domain.wordManager.tree_numbering import TreeNumbering
from io import BytesIO

from domain.parserManager.parser_word import ParserWord
from util.formula_helper import FormulaHelper

if __name__ == "__main__":
    def print_pretty_table(parsed_table: List[List[DataTable]]) -> None:
        """
        Красиво отображает таблицу в консоли с учётом объединений и разделений ячеек
        """
        if not parsed_table:
            print("Пустая таблица")
            return

        # Сначала вычисляем максимальные ширины для каждого столбца
        col_widths = {}
        for row in parsed_table:
            for j, cell in enumerate(row):
                if cell is None:
                    continue
                current_width = len(cell.data)
                if j not in col_widths or current_width > col_widths[j]:
                    col_widths[j] = current_width

        # Добавляем отступы (минимум 3 символа)
        col_widths = {k: max(v + 2, 8) for k, v in col_widths.items()}

        # Функция для создания горизонтальной границы
        def make_border():
            border = "+"
            for j in sorted(col_widths.keys()):
                border += "-" * col_widths[j] + "+"
            return border

        # Печатаем таблицу
        print(make_border())

        for i, row in enumerate(parsed_table):
            # Печатаем содержимое строки
            line = "|"
            for j, cell in enumerate(row):
                if cell is None:
                    # Пустая ячейка (часть объединённой)
                    line += " " * col_widths[j] + "|"
                else:
                    # Центрируем текст в ячейке
                    padding = col_widths[j] - len(cell.data)
                    left_pad = padding // 2
                    right_pad = padding - left_pad
                    line += " " * left_pad + cell.data+" "+f"({cell.parent_row} {cell.parent_col}" + " " * right_pad + "|"
            print(line)

            # Печатаем разделитель после строки
            print(make_border())

            # Обрабатываем вертикальные объединения
            for _ in range(1, 1):
                line = "|"
                for j, cell in enumerate(row):
                    if cell is None:
                        line += " " * col_widths[j] + "|"
                    else:
                        line += " " * col_widths[j] + "|"
                print(line)
                print(make_border())
    from io import BytesIO
    from PIL import Image as PILImage
    doc_manager = WordDocumentManager()
    doc_manager.load_document("tst.docx")
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    default_horizontal = WD_PARAGRAPH_ALIGNMENT.CENTER
    default_vertical = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    new_header = Header(level=1, text="Новый заголовок", children=[])
    doc_manager.add_element(None, new_header)

    # Создаем тестовое изображение
    img = PILImage.new('RGB', (100, 100), color='gray')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()

    # Добавление изображения под заголовок
    new_image = Image(image_data=image_data, caption="Новое изображение")
    new_imagdasde = Paragraph('dasdasd',None)
    new_imagdasdedsa = Paragraph('dasda32132131231sd',None)
    
    doc_manager.add_element(new_header, new_image)
    doc_manager.add_element(new_image, new_imagdasde)
    doc_manager.add_element(new_image, new_imagdasdedsa)
    new_header2 = Header(level=2, text="Новый222 заголовок", children=[])
    doc_manager.add_element(new_header, new_header2)
    new_imagdasdedsdsa = Paragraph('2020220',None)
    new_imagdasdedsdsa32 = Paragraph('2020220323232',None)
    doc_manager.add_element(new_header2, new_imagdasdedsdsa)
    doc_manager.add_element(new_imagdasdedsdsa, new_imagdasdedsdsa32)
    new_image1 = Image(image_data=image_data, caption="Новdsdasdое изображение")
    doc_manager.add_element(new_header, new_image1)
    
    new_header3 = Header(level=2, text="d заголовок", children=[])
    
    doc_manager.add_element(new_header, new_header3)
    doc_manager.add_element(new_header3,Formula('a-2=2','(dsad'))
    new_imagdasdedsds321a = Paragraph('321321321',None)
    doc_manager.add_element(new_header3, new_imagdasdedsds321a)
    new_header4 = Header(level=3, text="хитрый кейс3333 заголовок", children=[])
    doc_manager.add_element(new_header2,new_header4)
    new_imagdasdeddassds321a = Paragraph('[bnh эомент]',None)
    doc_manager.add_element(new_header4,new_imagdasdeddassds321a)

    new_header5 = Header(level=2, text="Ну если и это заголоовк мошны йто просто молчу", children=[])
    doc_manager.add_element(new_header,new_header5,new_header2)
    
    new_imagdasdedsds321adass = Paragraph('pusin',None)
    new_imagdasdedsds321adass1 = Paragraph('pusin2',None)
    new_imagdasdedsds321adass2 = Paragraph('pusin3',None)
    doc_manager.add_element(new_header5,new_imagdasdedsds321adass)
    doc_manager.add_element(new_imagdasdedsds321adass,new_imagdasdedsds321adass1)
    doc_manager.add_element(new_imagdasdedsds321adass,new_imagdasdedsds321adass2)


    new_header7 = Header(level=1, text="иди сюда заголовок", children=[])
    doc_manager.add_element(None, new_header7)
    new_header8 = Header(level=2, text="иди сюда заголовок 2", children=[])
    doc_manager.add_element(new_header7,new_header8)
    new_imagdasdedsds321adass2ds = Paragraph('susapusin3',None)
    doc_manager.add_element(new_header8,new_imagdasdedsds321adass2ds)

    new_header6 = Header(level=1, text="зайде укак я сюайд", children=[])
    doc_manager.add_element(None,new_header6,new_header)

    new_image3d21 = Image(image_data=image_data, caption="Новое изображение")
    new_image3d21dd = Image(image_data=image_data, caption="Новое 333изображение")

    doc_manager.add_element(new_imagdasdedsds321adass2ds,new_image3d21)
    new_header10 = Header(level=1, text="fasafasfafaf укак я сюайд", children=[])
    doc_manager.add_element(None,new_header10,new_header6)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,new_image3d21dd)
    lit= Listing("code dskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmaddskdmsakdmad","descriptio of code")    
    tab23 = Table([
        [DataTable("1", default_horizontal, default_vertical), DataTable("21", default_horizontal, default_vertical), DataTable("3", default_horizontal, default_vertical)],
        [DataTable("4", default_horizontal, default_vertical), DataTable("5", default_horizontal, default_vertical), DataTable("6", default_horizontal, default_vertical)]
    ],'описани таблицы офо')
    tab23e = Table( [
        [DataTable("1", default_horizontal, default_vertical), DataTable("32321", default_horizontal, default_vertical), DataTable("3", default_horizontal, default_vertical)],
        [DataTable("4", default_horizontal, default_vertical), DataTable("3213", default_horizontal, default_vertical), DataTable("6", default_horizontal, default_vertical)]
    ],'3213описани таблицы офо')
    tab23dase = Formula("E=mc^2","dasdas dsa21",None)
    tab2вы3dase = Formula("E=2332mc^2","d32321asdas dsa21",None)
    tab2вы3dasde = Formula("E=233d2mc^2","d32321asdas dsa21",None)
    
    doc_manager.add_element(new_imagdasdedsds321adass2ds,lit)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23e)
    doc_manager.add_element(new_imagdasdedsds321adass2ds,tab23dase)
    doc_manager.add_element(new_image3d21dd,tab2вы3dase)
    doc_manager.add_element(new_image3d21,tab2вы3dasde)
    test_para = Paragraph('after table?',None)
    lit2= Listing("code dadkmaskdm dsamk dksamkdasmdksajdaskdjnashdbasd jasnjdnasjkdnasjdnasdnasjkdnsadjasn jdsn adjasdnsaj ndjsak","doksddescriptio of code")    
    lit3= Listing("logc32131312ode dadkmaskdm dsamk dksamkdasmdksajdaskdjnashdbasd jasnjdnasjkdnasjdnasdnasjkdnsadjasn jdsn adjasdnsaj ndjsak","doksddescriptio of code")    
    
    doc_manager.add_element(lit,test_para)
    doc_manager.add_element(tab23e,lit2)
    doc_manager.add_element(new_header7,lit3)
    dod_lits = ListElement(['dal 1;',"dal 2;","dal 3."],'–')
    doc_manager.add_element(test_para,dod_lits)
    dkjsad2 = Paragraph('afet s2susapusin3',None)
    doc_manager.add_element(dod_lits,dkjsad2)
    img1 = PILImage.new('RGB', (100, 100), color='red')
    img_byte_arr1 = BytesIO()
    img1.save(img_byte_arr1, format='PNG')
    image_data1 = img_byte_arr1.getvalue()
    lodsds= ListElement(['первый;','второй;', "третий."],'–')
    
    # # Удаление изображения
    doc_manager.remove_element(new_header6)
    doc_manager.remove_element(lit2)
    doc_manager.remove_element(tab23dase)
    doc_manager.remove_element(dod_lits)
    doc_manager.remove_element(new_image3d21dd)
    doc_manager.remove_element(tab23e)
    doc_manager.add_element(lit3,lodsds)
    doc_manager.update_element(new_header10, Header(1,'проверка го гого'))
    doc_manager.add_element(new_header10,Paragraph(" ndskm"))
    doc_manager.update_element(new_header4, Header(1,'ну я хитрееее тебя 333проверка го гого'))
    doc_manager.update_element(dkjsad2, Paragraph("но вот и все par updated"))
    doc_manager.update_element(lodsds, ListElement(['как-то так;','пися231.'],'–'))
    doc_manager.update_element(lodsds, ListElement(['dsadasd;','как-то так;','пися231;','ага.'],'–'))
    doc_manager.update_element (new_image3d21, Image(image_data=image_data1, caption="red one Новое изображение"))

    doc_manager.update_element (tab23, Table([
        [DataTable("--3", default_horizontal, default_vertical), DataTable("21", default_horizontal, default_vertical), DataTable("3", default_horizontal, default_vertical)],
        [DataTable("4", default_horizontal, default_vertical), DataTable("425", default_horizontal, default_vertical), DataTable("652", default_horizontal, default_vertical)]
    ],'описани таблицы офо'))



    ds32 = Table( [
        [DataTable("01", default_horizontal, default_vertical), DataTable("1", default_horizontal, default_vertical)],
        [DataTable("02", default_horizontal, default_vertical), DataTable("2", default_horizontal, default_vertical)],
        [DataTable("3", default_horizontal, default_vertical), DataTable("3", default_horizontal, default_vertical)]
    ]," n ni niFracation table")
    doc_manager.add_element(new_header8,ds32)
    doc_manager.update_element (ds32, Table([
        [DataTable("10", default_horizontal, default_vertical), DataTable("10", default_horizontal, default_vertical)],
        [DataTable("20", default_horizontal, default_vertical), DataTable("20", default_horizontal, default_vertical)],
        [DataTable("20", default_horizontal, default_vertical), DataTable("20", default_horizontal, default_vertical)]
    ],"Fracat32ion table"))
    
    doc_manager.update_element(tab2вы3dase,Formula(r"\frac{1}{2}-\frac{\frac{10}{20}-}{}=30\begin{bmatrix} 1& 1 &1 1 \\ 1& 1 &1 1 \\ 1& 1 &1 1 \end{bmatrix}",''))
    doc_manager.add_element(tab2вы3dase,Paragraph('dksamdkasmdkasmdk amdk smadks amdksa mdkas mdask dms dkas'))
    doc_manager.update_element(lit3,Listing(f"poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas",'capton new one'))
    doc_manager.update_element(lit,Listing(f"3213123 1321poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas poso smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnasposo smskdmska dmsn dkasjndjkasjdnasjkdnjaksdnajnaskdjnasjkdn kdsna ksdnas",'32capton new one'))
    # doc_manager.remove_element(tab2вы3dasde)
    new_header103 = Header(level=3, text="toooto", children=[])

    doc_manager.add_element(new_header8,new_header103)
    doc_manager.add_element(new_header103,Paragraph("32131312412 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header103,Paragraph("dlasjd dk askdj lkasdно вот и все par updated"))
    new_header104 = Header(level=3, text="che dks", children=[])

    doc_manager.add_element(new_header8,new_header104,new_header103)
    doc_manager.add_element(new_header104,Paragraph("IMage knodskd skds;kdaskdkasd 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header104,Paragraph("dasindm; j1nj2eeio12e2m21eio dk askdj lkasdно вот и все par updated dasdasdd ajsdn jasdnjasndj ansdjasn dasnddddddddddddddddddddddddddddddddddsnj ndjs ndj sndj asndjsj"))
    new_header105 = Header(level=3, text="new_header105 che dks", children=[])

    doc_manager.add_element(new_header8,new_header105,new_header103)
    doc_manager.add_element(new_header105,Paragraph("new_header105 knodskd skds;kdaskdkasd 412 4214но вот и все par updated"))
    doc_manager.add_element(new_header105,Paragraph("new_header105; j1nj2eeio12e2m21eio dk askdj lkasdно вот и все par updated"))
    doc_manager.add_element(new_header105,Listing(f"""def move_element_word(self, parent: Element, element: Element, after:Element =None):
        if isinstance(element,Header):
            self.numberer.adjust_header_levels(parent,element)
        self.numberer.move_element(parent,element,after)
        if not isinstance(element,Header) and not isinstance(parent,Header):
            after=parent
        if isinstance(element,Header):
            self._sync_move_to_doc(element,parent,after,element,parent)
        else:
            self._sync_move_to_doc(element,parent,after,None,None)""",'cdasdapton new one')
)
    doc_manager.move_element_word(new_header4,new_header8)
    doc_manager.move_element_word(new_header,new_header8,new_header5)
    doc_manager.parser_word_manager.print_tree(doc_manager.tree)
    doc_manager.save_document()