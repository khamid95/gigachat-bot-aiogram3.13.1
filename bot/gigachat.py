import logging
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models import GigaChat
from bot.tokens import TokenManager
from typing import Tuple, Callable

logger = logging.getLogger(__name__)

class CustomGigaChat:
    """Класс для работы с GigaChat с учетом контекста"""
    def __init__(self, credentials: str, expert_prompt: str, user_id: str, token_limit: int):
        self.chat = GigaChat(credentials=credentials, verify_ssl_certs=False)
        self.conversation = []
        self.user_id = user_id
        self.token_manager = TokenManager(user_id, token_limit)
        if expert_prompt is not None:
            self.conversation.append(SystemMessage(content=expert_prompt))
            logger.info(f"Expert prompt инициализирован для user_id={user_id}")
        else:
            logger.warning(f"expert_prompt не инициализирован для user_id={user_id}")

    async def ask_a_question(self, message: str, count_tokens: Callable[[str], int]) -> Tuple[str, bool]:
        """Отправка запроса в GigaChat и получение ответа"""
        logger.debug(f"Обработка вопроса для user_id={self.user_id}: {message[:50]}...")
        tokens_in_message = count_tokens(message)
        
        self.conversation.append(HumanMessage(content=message))
        
        try:
            response = await self.chat.ainvoke(self.conversation)
            response_text = response.content
            response_tokens = count_tokens(response_text)
            
            total_tokens = tokens_in_message + response_tokens
            success = self.token_manager.add_tokens(total_tokens)
            
            self.conversation.append(response)
            logger.info(f"Получен ответ от GigaChat для user_id={self.user_id}: {response_text[:50]}...")
            
            return response_text, success
        except Exception as e:
            logger.error(f"Ошибка GigaChat для user_id={self.user_id}: {e}")
            self.conversation.pop()  # Удаляем вопрос при ошибке
            return f"Ошибка при обращении к GigaChat: {str(e)}", False

    async def reset_context(self):
        """Сброс контекста диалога, оставляя начальный промпт"""
        self.conversation = [self.conversation[0]] if self.conversation else []
        logger.info(f"Контекст сброшен для user_id={self.user_id}")
