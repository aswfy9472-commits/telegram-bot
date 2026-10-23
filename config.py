"""إعدادات المشروع."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# القالب الوحيد المعتمد (لا يتم تعديله أبداً، يُنسخ فقط).
TEMPLATE_PATH: Path = BASE_DIR / "template" / "template.docx"

TEMP_DIR: Path = BASE_DIR / "temp"
LOG_DIR: Path = BASE_DIR / "logs"
LOG_FILE: Path = LOG_DIR / "bot.log"

# مسار LibreOffice اختياري (إذا لم يُكتشف تلقائياً).
LIBREOFFICE_PATH: str = os.getenv("LIBREOFFICE_PATH", "").strip()

# أقصى عدد لعمليات LibreOffice المتزامنة (كل واحدة تستهلك ذاكرة).
MAX_CONCURRENT_CONVERSIONS: int = int(os.getenv("MAX_CONCURRENT_CONVERSIONS", "2"))
PDF_TIMEOUT_SECONDS: int = int(os.getenv("PDF_TIMEOUT_SECONDS", "180"))

# تنسيق محتوى التقرير
CONTENT_FONT_SIZE_PT: int = 14          # حجم الخط
CONTENT_LINE_SPACING: float = 1.5       # تباعد الأسطر

# حدود الإدخال
MAX_TITLE_LEN = 300
MAX_NAME_LEN = 120
MAX_CONTENT_LEN = 400_000

# رسالة تيليجرام الواحدة لا تتجاوز 4096 حرفاً؛ ما يقاربها يعني تقسيماً تلقائياً.
TELEGRAM_SPLIT_THRESHOLD = 4000
