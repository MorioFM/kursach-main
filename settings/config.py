"""
Конфигурация приложения
"""

# Настройки базы данных
import os
import sys

# Определяем путь к базе данных (работает и в dev, и после компиляации)
if getattr(sys, 'frozen', False):
    # Если приложение скомпилировано
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Если запускается из исходников
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_NAME = os.path.join(BASE_DIR, "kindergarten.db")

# Настройки интерфейса
APP_TITLE = "Учет детей в детском саду"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 1000

# Цвета
PRIMARY_COLOR = "#2196F3"
SECONDARY_COLOR = "#FFC107"
ERROR_COLOR = "#F44336"
SUCCESS_COLOR = "#4CAF50"

# Категории возраста
AGE_CATEGORIES = {
    "Ясельная (1-3 года)": "Ясельная (1-3 года)",
    "Младшая (3-4 года)": "Младшая (3-4 года)",
    "Средняя (4-5 лет)": "Средняя (4-5 лет)",
    "Старшая (5-6 лет)": "Старшая (5-6 лет)",
    "Подготовительная (6-7 лет)": "Подготовительная (6-7 лет)"
}

# Пол
GENDERS = {
    "М": "Мужской",
    "Ж": "Женский"
}
