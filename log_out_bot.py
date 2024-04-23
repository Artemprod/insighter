import asyncio

from aiogram import Bot

from settings import project_settings
from logging_module.log_config import insighter_logger





async def logout_bot():
    bot = Bot(token=project_settings.telegram_bot_token)
    try:
        await bot.log_out()
        insighter_logger.info("Бот успешно отключен от официального сервера Telegram.")
    except Exception as e:
        insighter_logger.info(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(logout_bot())
