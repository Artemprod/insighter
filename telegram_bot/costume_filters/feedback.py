
from aiogram.filters import BaseFilter
from aiogram.types import Message


class FeedbackCommandFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что в сообщении есть текст и он начинается с команды /feedback
        return message.text and message.text.startswith("/feedback")
