import logging
import os
from bot.database import SessionLocal, User

logger = logging.getLogger(__name__)

class TokenManager:
    """Класс для управления токенами пользователя"""
    def __init__(self, user_id: str, token_limit: int = None):
        self.user_id = user_id
        token_limit_str = os.getenv("TOKEN_LIMIT")
        if token_limit_str is None:
            raise ValueError("Переменная окружения TOKEN_LIMIT не задана в bot.env")
        self.token_limit = int(token_limit_str) if token_limit is None else token_limit
        self._load_tokens()

    def _load_tokens(self):
        """Загрузка текущего количества токенов из базы данных"""
        with SessionLocal() as session:
            user = session.query(User).filter_by(user_id=self.user_id).first()
            if user:
                self.total_tokens_used = user.total_tokens_used
                # Синхронизируем token_limit
                if user.token_limit != self.token_limit:
                    user.token_limit = self.token_limit
                    session.commit()
                    logger.info(f"Обновлён token_limit до {self.token_limit} для user_id={self.user_id}")
            else:
                self.total_tokens_used = 0

    def add_tokens(self, tokens: int) -> bool:
        """Добавление токенов и проверка лимита"""
        self.total_tokens_used += tokens
        with SessionLocal() as session:
            user = session.query(User).filter_by(user_id=self.user_id).first()
            if not user:
                user = User(user_id=self.user_id, total_tokens_used=0, token_limit=self.token_limit)
                session.add(user)
            user.total_tokens_used = self.total_tokens_used
            user.token_limit = self.token_limit
            session.commit()
        
        logger.info(f"Добавлено {tokens} токенов, total_tokens_used={self.total_tokens_used}, user_id={self.user_id}")
        if self.total_tokens_used > self.token_limit:
            logger.info(f"Лимит токенов превышен для user_id={self.user_id}")
            return False
        return True

    def get_remaining_tokens(self) -> int:
        """Получение оставшихся токенов"""
        remaining = self.token_limit - self.total_tokens_used
        logger.info(f"Осталось {remaining} токенов для user_id={self.user_id}")
        return remaining

    def reset_tokens(self):
        """Сброс токенов"""
        self.total_tokens_used = 0
        with SessionLocal() as session:
            user = session.query(User).filter_by(user_id=self.user_id).first()
            if user:
                user.total_tokens_used = 0
                user.token_limit = self.token_limit
                session.commit()
            logger.info(f"Токены сброшены для user_id={self.user_id}")
