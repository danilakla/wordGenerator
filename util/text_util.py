import re

class TextUtils:
    @staticmethod
    def extract_text_after_leading_numbers(text: str) -> str:
        """
        Remove leading numbers and dots from text (e.g., "1.2.3 Header" -> "Header")
        """
        cleaned_text = re.sub(r"^(\d+[\.\d]*\s*)+", "", text).strip()
        return cleaned_text if cleaned_text else text

    @staticmethod
    def clean_caption(caption: str) -> str:
        """
        Clean captions by removing pattern prefixes like "Table 1.2 - "
        """
        patterns = [
            r'^Таблица \d+\.\d+ – .+$',
            r'^Рисунок \d+\.\d+ – .+$',
            r'^Листинг \d+\.\d+ – .+$'
        ]
        if any(re.match(pattern, caption) for pattern in patterns):
            return caption.split(" – ", 1)[-1].strip()
        return caption