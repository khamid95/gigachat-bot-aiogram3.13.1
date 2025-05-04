import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

Base = declarative_base()
DB_PATH = "data/databot.db"
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    total_tokens_used = Column(Integer, default=0)
    token_limit = Column(Integer)  # Убрали default

class UserRequest(Base):
    __tablename__ = 'user_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String)
    query_time = Column(DateTime, default=datetime.utcnow)
    user_query = Column(String, nullable=False)
    ai_response = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)

def init_database():
    """Инициализация базы данных: создание таблиц и синхронизация token_limit"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        logger.info(f"База данных {DB_PATH} уже существует, использую существующую.")
    else:
        logger.info(f"База данных {DB_PATH} не найдена, создаю новую.")
    
    Base.metadata.create_all(engine)
    
    # Синхронизация token_limit
    token_limit_str = os.getenv("TOKEN_LIMIT")
    if token_limit_str is None:
        raise ValueError("Переменная окружения TOKEN_LIMIT не задана в bot.env")
    token_limit = int(token_limit_str)
    with SessionLocal() as session:
        users = session.query(User).all()
        for user in users:
            if user.token_limit != token_limit:
                user.token_limit = token_limit
                session.commit()
                logger.info(f"Обновлён token_limit до {token_limit} для user_id={user.user_id}")
    logger.info("Таблицы базы данных инициализированы.")

def save_to_db(user_id: str, username: str, user_query: str, ai_response: str, tokens_used: int):
    """Сохранение запроса и ответа в базу данных"""
    with SessionLocal() as session:
        user_request = UserRequest(
            user_id=user_id,
            username=username,
            query_time=datetime.utcnow(),
            user_query=user_query,
            ai_response=ai_response,
            tokens_used=tokens_used
        )
        session.add(user_request)
        
        # Обновляем total_tokens_used в users
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, total_tokens_used=0, token_limit=int(os.getenv("TOKEN_LIMIT")))
            session.add(user)
        user.total_tokens_used += tokens_used
        user.username = username
        
        session.commit()
        logger.debug(f"Сохранено для user_id={user_id}: tokens_used={tokens_used}")

def reset_user_tokens(user_id: str):
    """Сброс токенов пользователя в таблице users"""
    with SessionLocal() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.total_tokens_used = 0
            user.token_limit = int(os.getenv("TOKEN_LIMIT"))
            session.commit()
            logger.info(f"Токены сброшены для user_id={user_id}")
