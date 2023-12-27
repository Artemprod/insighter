import torch
import asyncio
import os.path

from aiogram import Bot, Dispatcher
from aiogram.client.session import aiohttp
from aiogram.client.telegram import TelegramAPIServer

from api.gpt import GPTAPIrequest
from api.media_recognition.recognition import  WhisperRecognitionAPI

from handlers import command_handler, docs_handlers
from handlers.summary_process import process_from_audo_handler, process_from_text
from insiht_bot_container import assistant_repo, config_data, user_repo, doc_repo, progress_bar
from keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.client.session.aiohttp import AiohttpSession

from midleware.attempts import CheckAttemptsMiddleware


async def main() -> None:
    t = torch

    root_dir = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))


    config = config_data  # Убедитесь, что config_data загружается правильно

    # Используем aiohttp с отключенным SSL
    connector = aiohttp.TCPConnector(ssl=False)
    aiohttp_session = aiohttp.ClientSession(connector=connector)
    session = AiohttpSession(api=TelegramAPIServer.from_base(config.telegram_server.URI), session=aiohttp_session)

    redis = Redis(host=config.redis_storage.main_bot_docker_host,
                  port=config.redis_storage.main_bot_docker_port)
    storage: RedisStorage = RedisStorage(redis=redis)


    assistant = GPTAPIrequest(api_key=config.ChatGPT.key )
    bot: Bot = Bot(token=config.Bot.tg_bot_token, parse_mode='HTML',session=session )
    wisper_model = WhisperRecognitionAPI()
    # vosk_model = VoskRecognition()

    # Добовляем хэгдлеры в диспечтер через роутеры
    dp: Dispatcher = Dispatcher(storage=storage,media_recognition=wisper_model, root_dir=root_dir,
                                assistant_repo=assistant_repo, user_repo=user_repo,
                                doc_repo=doc_repo, assistant=assistant,
                                progress_bar=progress_bar)

    dp.include_router(command_handler.router)
    dp.include_router(process_from_audo_handler.router)
    dp.include_router(process_from_text.router)
    dp.include_router(docs_handlers.router)
    dp.update.outer_middleware(CheckAttemptsMiddleware(user_repo=user_repo))

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем прослушку бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Запускаем бота
    asyncio.run(main())
