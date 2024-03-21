
from aiogram.filters import BaseFilter
from aiogram.types import Message


class TariffCommandFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что в сообщении есть текст и он начинается с команды /feedback
        return message.text and message.text.startswith("/tariff")


class PaymentInfoCommandFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что в сообщении есть текст и он начинается с команды /feedback
        return message.text and message.text.startswith("/terms")


class BuyCommandFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что в сообщении есть текст и он начинается с команды /feedback
        return message.text and message.text.startswith("/buy")
