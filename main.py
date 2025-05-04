import asyncio
import logging
import os
from aiogram import Bot
from bot.bot import TelegramBot
from bot.database import init_database
from bot.utils import load_expert_prompt
from bot.services import GigaChatService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция для запуска бота"""
    # Проверка переменных окружения
    required_env_vars = ["BOT_TOKEN", "GIGACHAT_CREDENTIALS", "GOOGLE_DOC_URL", "TOKEN_LIMIT", "START_MESSAGE"]
    missing_vars = [var for var in required_env_vars if os.getenv(var) is None]
    if missing_vars:
        logger.error(f"Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        raise ValueError(f"Необходимо задать все переменные окружения в bot.env: {', '.join(missing_vars)}")

    init_database()
    
    bot_token = os.getenv("BOT_TOKEN")
    google_doc_url = os.getenv("GOOGLE_DOC_URL")
    start_message = os.getenv("START_MESSAGE")
    
    bot = Bot(token=bot_token)
    expert_prompt = await load_expert_prompt(google_doc_url)
    gigachat_service = GigaChatService(bot, google_doc_url, expert_prompt)
    telegram_bot = TelegramBot(bot_token, gigachat_service, start_message)
    
    try:
        logger.info("Запуск polling...")
        await telegram_bot.get_dispatcher().start_polling(telegram_bot.bot)
    finally:
        await telegram_bot.bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
