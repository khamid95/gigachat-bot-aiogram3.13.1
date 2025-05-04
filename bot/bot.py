import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from bot.handlers import TelegramHandlers
from bot.services import GigaChatService
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramBot:
    """Класс для управления Telegram-ботом"""
    def __init__(self, token: str, gigachat_service: GigaChatService, start_message: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.handlers = TelegramHandlers(self.bot, gigachat_service, start_message)
        
        # Регистрация обработчиков
        self.dp.message.register(self.handlers.cmd_start, CommandStart())
        self.dp.message.register(self.handlers.reset_dialog, lambda message: message.text == "🔁 Обновить диалог")
        self.dp.message.register(self.handlers.ai_dialog)

    def get_dispatcher(self) -> Dispatcher:
        """Получение диспетчера для polling"""
        return self.dp
