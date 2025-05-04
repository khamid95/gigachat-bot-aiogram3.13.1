import logging
import os
from typing import Dict, Optional, Tuple
from aiogram import Bot
from aiogram.types import Message
from bot.database import save_to_db, reset_user_tokens
from bot.utils import count_tokens
from bot.gigachat import CustomGigaChat

logger = logging.getLogger(__name__)

class GigaChatService:
    """Сервис для работы с GigaChat и токенами"""
    def __init__(self, bot: Bot, google_doc_url: str, expert_prompt: Optional[str]):
        self.bot = bot
        self.google_doc_url = google_doc_url
        self.expert_prompt = expert_prompt
        self.user_gigachat: Dict[int, CustomGigaChat] = {}
        token_limit_str = os.getenv("TOKEN_LIMIT")
        if token_limit_str is None:
            raise ValueError("Переменная окружения TOKEN_LIMIT не задана в bot.env")
        self.token_limit = int(token_limit_str)

    async def initialize_user(self, user_id: int, username: str) -> Optional[CustomGigaChat]:
        """Инициализация GigaChat для нового пользователя"""
        if user_id not in self.user_gigachat:
            if self.expert_prompt is None:
                return None
            self.user_gigachat[user_id] = CustomGigaChat(
                credentials=os.getenv("GIGACHAT_CREDENTIALS"),
                expert_prompt=self.expert_prompt,
                user_id=str(user_id),
                token_limit=self.token_limit
            )
        return self.user_gigachat[user_id]

    async def delete_wait_message(self, message: Message, wait_message: Optional[Message]) -> None:
        """Удаление сообщения 'Ожидайте ответ'"""
        if wait_message:
            try:
                await self.bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение 'Ожидайте ответ' для {message.from_user.id}: {e}")

    async def process_tokens(self, user_id: int, username: str, user_message: str, response: str) -> None:
        """Обработка токенов и сохранение в базу"""
        tokens_used = count_tokens(user_message) + count_tokens(response)
        save_to_db(str(user_id), username, user_message, response, tokens_used)

    async def notify_low_tokens(self, user_id: int, chat_id: int) -> None:
        """Отправка уведомления о низком количестве токенов"""
        if user_id in self.user_gigachat:
            remaining_tokens = self.user_gigachat[user_id].token_manager.get_remaining_tokens()
            if remaining_tokens < 100:
                await self.bot.send_message(chat_id=chat_id, text="🔴 Память заканчивается. Скоро диалог начнётся заново.")

    async def process_message(self, user_id: int, username: str, user_message: str) -> Tuple[str, bool]:
        """Обработка сообщения через GigaChat"""
        gigachat = await self.initialize_user(user_id, username)
        if gigachat is None:
            return "Бот еще не готов к работе, попробуйте позже.", False
        
        response, success = await gigachat.ask_a_question(user_message, count_tokens)
        await self.process_tokens(user_id, username, user_message, response)
        
        if not success and user_id in self.user_gigachat:
            await gigachat.reset_context()
            gigachat.token_manager.reset_tokens()
            reset_user_tokens(str(user_id))
        
        return response, success

    async def reset_user_tokens(self, user_id: int, username: str) -> None:
        """Сброс токенов и контекста для пользователя"""
        if user_id in self.user_gigachat:
            await self.user_gigachat[user_id].reset_context()
            self.user_gigachat[user_id].token_manager.reset_tokens()
            reset_user_tokens(str(user_id))
