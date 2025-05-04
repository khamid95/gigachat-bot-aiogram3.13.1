import logging
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from bot.services import GigaChatService
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramHandlers:
    """Класс для обработки сообщений и команд Telegram"""
    def __init__(self, bot: Bot, gigachat_service: GigaChatService, start_message: str):
        self.bot = bot
        self.gigachat_service = gigachat_service
        self.start_message = start_message
        # Создаём клавиатуру с кнопкой
        self.keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔁 Обновить диалог")]],
            resize_keyboard=True,
            one_time_keyboard=False
        )

    async def cmd_start(self, message: Message) -> None:
        """Обработчик команды /start"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or 'Anonymous'
            await self.gigachat_service.reset_user_tokens(user_id, username)
            await message.answer(self.start_message, reply_markup=self.keyboard)
        except Exception as e:
            logger.error(f"Ошибка в cmd_start: {e}")
            await message.answer("Произошла ошибка при запуске бота. Попробуйте позже.")

    async def reset_dialog(self, message: Message) -> None:
        """Обработчик кнопки '🔁 Обновить диалог'"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or 'Anonymous'
            await self.gigachat_service.reset_user_tokens(user_id, username)
            await message.answer("🔁 Память обновлена. Диалог начат заново.", reply_markup=self.keyboard)
        except Exception as e:
            logger.error(f"Ошибка в reset_dialog для user_id={user_id}: {e}")
            await message.answer("Произошла ошибка при обновлении диалога. Попробуйте позже.")

    async def ai_dialog(self, message: Message) -> None:
        """Обработчик текстовых сообщений для диалога с GigaChat"""
        if not message.text:
            return

        wait_message = None
        try:
            user_id = message.from_user.id
            username = message.from_user.username or 'Anonymous'
            user_message = message.text

            wait_message = await message.answer("⏳ Ожидайте ответ...")
            response, success = await self.gigachat_service.process_message(user_id, username, user_message)
            
            await self.gigachat_service.delete_wait_message(message, wait_message)
            await message.answer(response, reply_markup=self.keyboard)
            
            if success:
                await self.gigachat_service.notify_low_tokens(user_id, message.chat.id)
            else:
                await message.answer("🔁 Память обновлена. Диалог начат заново.", reply_markup=self.keyboard)

        except Exception as e:
            await self.gigachat_service.delete_wait_message(message, wait_message)
            if "rate limit exceeded" in str(e).lower():
                await message.answer("Лимит токенов GigaChat исчерпан. Попробуйте позже!", reply_markup=self.keyboard)
            else:
                logger.error(f"Ошибка в ai_dialog для {user_id}: {e}")
                if not str(e).startswith("Telegram server says - Bad Request: message to delete not found"):
                    await message.answer("Произошла ошибка. Попробуйте позже.", reply_markup=self.keyboard)
