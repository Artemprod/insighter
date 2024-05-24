import asyncio
import os.path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import Redis, RedisStorage

from enteties.queue_entity import PipelineQueues
from telegram_bot.handlers import (
    payment_handler,
)
from telegram_bot.handlers import docs_handlers, command_handler, process_file_handler
from insiht_bot_container import (
    assistant_repository,
    config_data,
    document_repository,
    file_format_manager,
    gpt_dispatcher_only_longcahin,
    progress_bar,
    server_file_manager,
    tariff_repository,
    text_invoker,
    transaction_repository,
    user_balance_repo,
    user_repository,
    whisper_post_processor, mixpanel_tracker, gpt_dispatcher_bare_model_4o,
)
from logging_module.log_config import insighter_logger
from main_process.process_pipline import ProcesQueuePipline
from telegram_bot.keyboards.main_menu import set_main_menu
from telegram_bot.midleware.antiflood import AntiFloodMiddleware
from telegram_bot.midleware.attempts import CheckAttemptsMiddleware


async def create_bot(queue_pipeline) -> None:
    root_dir = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

    config = config_data
    session = AiohttpSession(api=TelegramAPIServer.from_base(config.telegram_server.URI))
    system_type = config_data.system.system_type

    if system_type == "local":
        dp: Dispatcher = Dispatcher(
            root_dir=root_dir,
            assistant_repository=assistant_repository,
            user_repository=user_repository,
            document_repository=document_repository,
            process_queue=queue_pipeline,
            progress_bar=progress_bar,
            user_balance_repo=user_balance_repo,
            transaction_repository=transaction_repository,
            tariff_repository=tariff_repository,
            mixpanel_tracker=mixpanel_tracker
        )
        insighter_logger.info("local system initialized")

    elif system_type == "docker":
        redis = Redis(
            host=config.redis_storage.main_bot_docker_host,
            port=config.redis_storage.main_bot_docker_port,
        )
        storage: RedisStorage = RedisStorage(redis=redis)
        dp: Dispatcher = Dispatcher(
            storage=storage,
            root_dir=root_dir,
            assistant_repository=assistant_repository,
            user_repository=user_repository,
            document_repository=document_repository,
            process_queue=queue_pipeline,
            progress_bar=progress_bar,
            user_balance_repo=user_balance_repo,
            transaction_repository=transaction_repository,
            tariff_repository=tariff_repository,
            mixpanel_tracker=mixpanel_tracker
        )
        insighter_logger.info("docker system initialized")
    bot: Bot = Bot(token=config.Bot.tg_bot_token,
                   default=DefaultBotProperties(parse_mode="HTML"),
                   session=session)

    # Добовляем хэгдлеры в диспечтер через роутеры
    dp.include_router(command_handler.router)
    dp.include_router(process_file_handler.router)
    dp.include_router(docs_handlers.router)
    dp.include_router(payment_handler.router)
    dp.update.outer_middleware(AntiFloodMiddleware())
    dp.update.outer_middleware(CheckAttemptsMiddleware(user_repository=user_repository, balance_repo=user_balance_repo))

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем прослушку бота
    await dp.start_polling(bot)


async def create_pipline_processes(queue_pipeline) -> None:
    pipeline_process = ProcesQueuePipline(
        queue_pipeline=queue_pipeline,
        database_document_repository=document_repository,
        server_file_manager=server_file_manager,
        text_invoker=text_invoker,
        ai_llm_request=gpt_dispatcher_bare_model_4o,
        format_definer=file_format_manager,
        progress_bar=progress_bar,
        config_data=config_data,
        post_processor=whisper_post_processor,
    )
    await pipeline_process.run_process()


async def main():
    loop = asyncio.get_running_loop()
    queue_pipeline = PipelineQueues(loop=loop)
    bot_task = asyncio.create_task(create_bot(queue_pipeline=queue_pipeline))
    pipline_task = asyncio.create_task(create_pipline_processes(queue_pipeline=queue_pipeline))
    insighter_logger.info("Bot is started")
    await bot_task
    await pipline_task


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
