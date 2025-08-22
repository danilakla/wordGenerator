import sys
import tempfile
import os
from pathlib import Path
from docx2pdf import convert
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QPushButton, QWidget, QLabel, QScrollArea,
                            QHBoxLayout, QSizePolicy, QScrollBar)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import fitz  # PyMuPDF

class DocxViewer(QMainWindow):
    def __init__(self, docx_document):
        super().__init__()
        self.docx_doc = docx_document
        self.current_page = 0
        self.total_pages = 0
        self.temp_files_to_cleanup = []  # Список для очистки
        self.pdf_pages = []  # Список для хранения всех страниц PDF
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("DOCX Viewer with Multi-page PDF")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Кнопка для показа
        self.btn_show = QPushButton("Показать документ")
        layout.addWidget(self.btn_show)
        
        # Индикатор страницы
        self.page_label = QLabel("Страница: 0/0")
        layout.addWidget(self.page_label)
        
        # Область для отображения со скроллом
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Контейнер для всех страниц
        self.pdf_container = QWidget()
        self.pdf_layout = QVBoxLayout(self.pdf_container)
        self.pdf_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.pdf_container)
        layout.addWidget(self.scroll_area)
        
        central_widget.setLayout(layout)
        
        # Подключение сигналов
        self.btn_show.clicked.connect(self.show_document)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
    def show_document(self):
        """Создает временные файлы и показывает документ"""
        # Очищаем предыдущие данные
        self.cleanup_temp_files()
        self.clear_pdf_pages()
        
        temp_docx_path = None
        temp_pdf_path = None
        
        try:
            # 1. Сохраняем doc во временный DOCX
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                temp_docx_path = temp_docx.name
                self.docx_doc.save(temp_docx_path)
            
            # 2. Создаем временный PDF файл
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
            
            # 3. Конвертируем DOCX в PDF
            convert(temp_docx_path, temp_pdf_path)
            
            # 4. Сохраняем пути для последующей очистки
            self.temp_files_to_cleanup.extend([temp_docx_path, temp_pdf_path])
            self.current_pdf_path = temp_pdf_path
            
            # 5. Загружаем все страницы PDF
            self.load_all_pdf_pages()
            
        except Exception as e:
            print(f"Ошибка: {e}")
                
    def load_all_pdf_pages(self):
        """Загружает все страницы PDF и отображает их"""
        try:
            doc = fitz.open(self.current_pdf_path)
            self.total_pages = len(doc)
            
            # Очищаем контейнер
            self.clear_pdf_pages()
            self.pdf_pages = []
            
            # Загружаем все страницы
            for page_number in range(self.total_pages):
                page = doc.load_page(page_number)
                
                # Конвертируем в изображение
                mat = fitz.Matrix(2, 2)  # Увеличение для качества
                pix = page.get_pixmap(matrix=mat)
                
                # Конвертируем в QPixmap
                img_data = pix.tobytes("ppm")
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                
                # Масштабируем
                scaled_pixmap = pixmap.scaled(800, 1000, 
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                
                # Создаем QLabel для каждой страницы
                page_label = QLabel()
                page_label.setPixmap(scaled_pixmap)
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                page_label.setStyleSheet("margin: 10px; border: 1px solid #ccc;")
                page_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                
                # Сохраняем ссылку и добавляем в layout
                self.pdf_pages.append(page_label)
                self.pdf_layout.addWidget(page_label)
            
            # Обновляем информацию о странице
            self.update_page_info(0)
            
        except Exception as e:
            print(f"Ошибка загрузки страниц: {e}")
    
    def on_scroll(self):
        """Обработчик скролла для определения текущей страницы"""
        if not self.pdf_pages:
            return
            
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_position = scroll_bar.value()
        
        # Определяем текущую страницу на основе позиции скролла
        current_page = 0
        max_visible_area = 0
        
        for i, page_label in enumerate(self.pdf_pages):
            page_pos = page_label.mapTo(self.scroll_area, page_label.pos()).y()
            page_height = page_label.height()
            
            # Проверяем, какая страница занимает большую часть видимой области
            visible_height = min(page_pos + page_height, scroll_position + self.scroll_area.height()) - max(page_pos, scroll_position)
            if visible_height > max_visible_area:
                max_visible_area = visible_height
                current_page = i
        
        if current_page != self.current_page:
            self.current_page = current_page
            self.update_page_info(current_page)
    
    def update_page_info(self, page_number):
        """Обновляет информацию о текущей странице"""
        self.page_label.setText(f"Страница: {page_number + 1}/{self.total_pages}")
    
    def clear_pdf_pages(self):
        """Очищает все страницы из контейнера"""
        for i in reversed(range(self.pdf_layout.count())): 
            widget = self.pdf_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.pdf_pages = []
    
    def cleanup_temp_files(self):
        """Очистка временных файлов"""
        files_to_remove = self.temp_files_to_cleanup.copy()
        self.temp_files_to_cleanup = []
        
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    print(f"Удален временный файл: {file_path}")
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")
    
    def closeEvent(self, event):
        """При закрытии приложения удаляем все временные файлы"""
        self.cleanup_temp_files()
        event.accept()

# Пример использования
if __name__ == "__main__":
    # Создаем тестовый многостраничный документ
    from docx import Document
    
    doc = Document("test.docx")
    
    app = QApplication(sys.argv)
    window = DocxViewer(doc)
    window.show()
    sys.exit(app.exec())