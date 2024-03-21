import asyncio

from aiogram import Bot

from insiht_bot_container import config_data
from logging_module.log_config import insighter_logger


async def logout_bot():
    config = config_data
    bot = Bot(token=config.Bot.tg_bot_token)
    try:
        await bot.log_out()
        insighter_logger.info("Бот успешно отключен от официального сервера Telegram.")
    except Exception as e:
        insighter_logger.info(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(logout_bot())
