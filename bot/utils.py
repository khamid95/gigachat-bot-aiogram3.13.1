import asyncio
import re
import aiohttp

async def load_prompt(url):
    """Загрузка промпта из Google Docs"""
    try:
        match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
        if match_ is None:
            raise ValueError('Invalid Google Docs URL')
        doc_id = match_.group(1)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt', timeout=10) as response:
                response.raise_for_status()
                return await response.text()
    except Exception as e:
        print(f"Ошибка при загрузке промпта: {str(e)}")
        return None

async def load_expert_prompt(url):
    """Загрузка начального промпта для GigaChat"""
    expert_prompt = await asyncio.wait_for(load_prompt(url), timeout=30)
    if expert_prompt is None:
        print("Не удалось загрузить expert_prompt. Бот начнет работу без него.")
    else:
        print("Загруженный промпт:", expert_prompt[:100])
    return expert_prompt

def count_tokens(text):
    """Подсчет токенов в тексте"""
    return len(text.split())
