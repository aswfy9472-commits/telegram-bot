"""نقطة تشغيل البوت: python bot.py"""
from __future__ import annotations

import logging
import logging.handlers
import sys

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import config
from handlers.help import help_command
from handlers.report import build_conversation_handler, cancel
from handlers.start import start_command
from services import file_manager
from services.pdf_converter import find_libreoffice, libreoffice_math_available

logger = logging.getLogger("bot")


class _RedactTokenFilter(logging.Filter):
    """يمنع ظهور BOT_TOKEN في السجلات مهما كان مصدر الرسالة."""

    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token

    def filter(self, record: logging.LogRecord) -> bool:
        if self.token:
            try:
                msg = record.getMessage()
            except Exception:
                return True
            if self.token in msg:
                record.msg = msg.replace(self.token, "***")
                record.args = ()
        return True


def setup_logging() -> None:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    redact = _RedactTokenFilter(config.BOT_TOKEN)
    for h in (file_handler, console):
        h.addFilter(redact)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [file_handler, console]
    # مكتبات الشبكة تطبع عناوين تحتوي التوكن في مستوى INFO
    for noisy in ("httpx", "httpcore", "telegram.ext.Application"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يسجل الخطأ للمطور فقط ولا يعرض أي تفاصيل تقنية للمستخدم."""
    logger.error("خطأ غير معالج", exc_info=context.error)


async def stale_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """زر قديم لا ينتمي لجلسة حالية (مثلاً بعد إعادة تشغيل البوت)."""
    query = update.callback_query
    if query:
        try:
            await query.answer("انتهت هذه الجلسة. أرسل /start للبدء من جديد.", show_alert=True)
        except Exception:
            pass


async def post_init(app: Application) -> None:
    file_manager.cleanup_stale_jobs()
    if not config.TEMPLATE_PATH.is_file():
        logger.warning("القالب غير موجود: %s", config.TEMPLATE_PATH)
    soffice = find_libreoffice()
    if not soffice:
        logger.warning("LibreOffice غير مثبت: لن يعمل تحويل PDF (راجع README).")
    else:
        logger.info("LibreOffice: %s", soffice)
        if libreoffice_math_available() is False:
            logger.warning(
                "مكوّن LibreOffice Math غير مثبت: ستختفي المعادلات من ملف PDF "
                "(على Linux ثبّت الحزمة libreoffice-math)."
            )


def main() -> None:
    setup_logging()
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("BOT_TOKEN غير مضبوط. ضعه في ملف .env (راجع README).")
        sys.exit(1)

    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .concurrent_updates(True)  # كي لا يوقف إنشاء تقرير مستخدم بقية المستخدمين
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(60)
        .pool_timeout(30)
        .post_init(post_init)
        .build()
    )

    app.add_handler(build_conversation_handler())
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(stale_button))
    app.add_error_handler(on_error)

    logger.info("البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
