# Telegram-бот с интеграцией GigaChat

Телеграм-бот, построенный на Aiogram 3.13.1. Работает с API GigaChat.

## Требования

- Docker
- Python 3.12 (для запуска без Docker)
- Аккаунты Telegram и Сбер для разработчиков

## Функционал и система токенов

Бот ведёт диалог с помощью ИИ GigaChat по промпту из Google Документа. Реализована система токенов (1 токен ≈ 1 слово) для контроля длины диалога и расхода API GigaChat. При остатке менее 100 токенов пользователь получает предупреждение. При превышении лимита контекст сбрасывается, и диалог начинается заново. Лимит токенов настраивается.

Бот сохраняет вопросы и ответы в базе SQLite в директории `data`, где также учитываются токены пользователей.

## Настройка

Создайте файл `bot.env` с токеном Telegram-бота (из [@BotFather](https://t.me/BotFather)), API GigaChat (из [Сбер для разработчиков](https://developers.sber.ru/)), ссылкой на Google Документ с промптом (не забудьте открыть доступ по ссылке), лимитом токенов и приветственным сообщением. Пример:

```bash
BOT_TOKEN=7661167373:your_bot_token
GIGACHAT_CREDENTIALS=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
GOOGLE_DOC_URL=https://docs.google.com/document/d/your-google-doc-id/edit
TOKEN_LIMIT=2000
START_MESSAGE=🔵Здравствуйте! Это AI-консультант. Я отвечу на ваши вопросы с помощью искусственного интеллекта.
```
## Запуск через Docker

1. Сборка образа:
```bash
docker build -t gigachat-bot .
```
2. Запуск контейнера:
```bash
docker run --name gigachat-bot-container -d --env-file bot.env -v $(pwd)/data:/app/data gigachat-bot
```
3. Проверка логов:
```bash
docker logs -f gigachat-bot-container
```

## Пример использования
Функционал интегрирован в бот для бронирования студии барабанщиков "GrowBeat" (Екатеринбург). Бот выступает консультантом, рассказывая о ценах, оборудовании, адресе, часах работы, преподавателе и методике обучения. Посмотреть можно здесь:
[@ritmoVED_bot](https://t.me/ritmoVED_bot)
