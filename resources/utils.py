import os
from datetime import datetime

def safe_parse_date(date_str):
    """Преобразует строку в дату. При ошибке возвращает None."""
    if not date_str or pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    # Пробуем разные форматы
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y', '%d.%m.%Y %H:%M:%S'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    # Специальный случай: "30.02.2025" -> исправляем на 28.02.2025
    if date_str.startswith('30.02.'):
        date_str = '28.02.' + date_str[6:]
        return datetime.strptime(date_str, '%d.%m.%Y').date()
    return None

def get_image_path(photo_filename):
    """Возвращает полный путь к файлу изображения товара."""
    if not photo_filename:
        return None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'resources', 'product_images', photo_filename)