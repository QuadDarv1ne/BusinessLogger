from loguru import logger
import sys
import signal
from src.bot import dp, bot

def handle_shutdown(signal, frame):
    """Функция для корректного завершения работы бота при получении сигнала остановки."""
    logger.info("Bot is shutting down gracefully...")
    dp.stop_polling()  # Останавливаем polling
    logger.info("Bot stopped.")

if __name__ == "__main__":
    # Настройка логирования
    logger.add("bot_logs.log", rotation="1 week", retention="30 days", compression="zip")
    logger.info("Starting bot...")

    # Добавление обработки сигнала для graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        dp.run_polling(
            bot,
            allowed_updates=[
                "callback_query",
                "business_message",
                "edited_business_message",
                "deleted_business_messages",
            ]
        )
    except Exception as e:
        logger.exception(f"An error occurred while running the bot: {e}")
        sys.exit(1)  # Выход с ошибкой, если не удается запустить бота
