
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, ContentType, Message
from environs import Env

from api.progress_bar.command import ProgressBarClient
from DB.Mongo.mongo_db import (
    MongoAssistantRepositoryORM,
    MongoUserRepoORM,
    UserBalanceRepoORM,
    UserDocsRepoORM,
)
from lexicon.LEXICON_RU import LEXICON_RU, TIME_ERROR_MESSAGE
from logging_module.log_config import insighter_logger
from main_process.ChatGPT.gpt_models_information import GPTModelManager
from main_process.process_pipline import PipelineData, PipelineQueues
from telegram_bot.keyboards.calback_factories import AssistantCallbackFactory
from telegram_bot.keyboards.inline_keyboards import (
    crete_inline_keyboard_assistants,
    crete_inline_keyboard_back_from_loading,
    crete_inline_keyboard_payed,
)
from telegram_bot.services.service_functions import (
    calculate_gpt_cost_with_tiktoken,
    calculate_whisper_cost,
    compare_user_minutes_and_file,
    estimate_gen_summary_duration,
    estimate_media_duration_in_minutes,
    format_filter,
    from_pipeline_data_object,
    generate_text_file,
    seconds_to_min_sec,
)
from telegram_bot.states.summary_from_audio import FSMSummaryFromAudioScenario

# Повесить мидлварь только на этот роутер
router = Router()
env: Env = Env()
env.read_env(".env")


@router.callback_query(AssistantCallbackFactory.filter())
async def processed_gen_answer(
    callback: CallbackQuery,
    callback_data: AssistantCallbackFactory,
    state: FSMContext,
    assistant_repository: MongoAssistantRepositoryORM,
    user_repository: MongoUserRepoORM,
):
    # Проверяем, есть ли текст в сообщении
    if callback.message.text:
        message = await callback.message.edit_text(
            text=LEXICON_RU.get("instructions", "как дела ?"),
            reply_markup=crete_inline_keyboard_back_from_loading(),
        )

    else:
        message = await callback.message.answer(
            text=LEXICON_RU.get("instructions", "как дела ?"),
            reply_markup=crete_inline_keyboard_back_from_loading(),
        )
    # записываем имя асистента пользователью
    assistant_name = await assistant_repository.get_assistant_name(assistant_id=callback_data.assistant_id)
    await user_repository.add_assistant_call_to_user(user_tg_id=callback.from_user.id, assistant_name=assistant_name)
    await state.update_data(
        assistant_id=callback_data.assistant_id,
        instruction_message_id=message.message_id,
    )
    await state.set_state(FSMSummaryFromAudioScenario.load_file)
    await callback.answer()


@router.message(
    FSMSummaryFromAudioScenario.load_file,
    ~F.content_type.in_(
        {
            ContentType.VOICE,
            ContentType.AUDIO,
            ContentType.VIDEO,
            ContentType.DOCUMENT,
        }
    ),
)
async def wrong_file_format(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await bot.send_message(
        chat_id=message.chat.id,
        text=LEXICON_RU["wrong_format"].format(
            income_file_format=message.content_type,
            actual_formats=LEXICON_RU["actual_formats"],
        ),
    )


@router.message(
    FSMSummaryFromAudioScenario.load_file,
    F.content_type.in_(
        {
            ContentType.VOICE,
            ContentType.AUDIO,
            ContentType.VIDEO,
            ContentType.DOCUMENT,
        }
    ),
)
async def processed_load_file(
    message: Message,
    bot: Bot,
    state: FSMContext,
    assistant_repository: MongoAssistantRepositoryORM,
    user_repository: MongoUserRepoORM,
    progress_bar: ProgressBarClient,
    process_queue: PipelineQueues,
    user_balance_repo: UserBalanceRepoORM,
    document_repository: UserDocsRepoORM,
):
    data = await state.get_data()
    assistant_id = data.get("assistant_id")
    instruction_message_id = int(data.get("instruction_message_id"))
    try:
        file_data = await format_filter(message=message, bot=bot, state=state)
        if file_data:
            file_path, income_file_format = file_data
            file_duration = await estimate_media_duration_in_minutes(bot=bot, message=message)
            # Проверяем есть ли минуты
            checking = await compare_user_minutes_and_file(
                user_tg_id=message.from_user.id,
                file_duration=file_duration,
                user_balance_repo=user_balance_repo,
            )
            if checking >= 0:
                # await check_if_i_can_load()
                if instruction_message_id:
                    try:
                        await bot.delete_message(
                            chat_id=message.chat.id,
                            message_id=instruction_message_id,
                        )
                    except TelegramBadRequest as e:
                        insighter_logger.exception(f"Ошибка при попытке удалить сообщение: {e}")

                # Form data to summary pipline
                pipline_object = await from_pipeline_data_object(
                    message=message,
                    bot=bot,
                    assistant_id=assistant_id,
                    fsm_state=state,
                    file_duration=file_duration,
                    file_path=file_path,
                    file_type=income_file_format,
                    additional_system_information=None,
                    additional_user_information=None,
                )

                # Start pipline process
                await process_queue.income_items_queue.put(pipline_object)
                await state.set_state(FSMSummaryFromAudioScenario.get_result)
                # Переход в новый стату вызов функции явно
                await processed_do_ai_conversation(
                    message=message,
                    state=state,
                    user_repository=user_repository,
                    bot=bot,
                    assistant_repository=assistant_repository,
                    progress_bar=progress_bar,
                    process_queue=process_queue,
                    user_balance_repo=user_balance_repo,
                    document_repository=document_repository,
                )
            else:
                keyboard = crete_inline_keyboard_payed()

                await message.bot.send_message(
                    chat_id=message.chat.id,
                    text=TIME_ERROR_MESSAGE.format(time=await seconds_to_min_sec(abs(checking))),
                )
                await message.answer_contact(
                    phone_number="+79896186869",
                    first_name="Александр",
                    last_name="Чернышов",
                    reply_markup=keyboard,
                )
    except Exception as e:
        insighter_logger.exception("Sommthing happend in defining format file ", e)
        await bot.delete_message(message_id=instruction_message_id, chat_id=message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=LEXICON_RU["error_message"])
        await state.set_state(FSMSummaryFromAudioScenario.load_file)


@router.message(FSMSummaryFromAudioScenario.get_result)
async def processed_do_ai_conversation(
    message: Message,
    bot: Bot,
    state: FSMContext,
    assistant_repository: MongoAssistantRepositoryORM,
    user_repository: MongoUserRepoORM,
    progress_bar: ProgressBarClient,
    process_queue: PipelineQueues,
    user_balance_repo: UserBalanceRepoORM,
    document_repository: UserDocsRepoORM,
):
    transcribed_text_data: PipelineData = await process_queue.transcribed_text_sender_queue.get()
    if transcribed_text_data.transcribed_text:
        file_in_memory, file_name = await generate_text_file(
            content=transcribed_text_data.transcribed_text,
            message_event=message,
        )

        await bot.send_document(
            chat_id=transcribed_text_data.telegram_message.chat.id,
            document=BufferedInputFile(file=file_in_memory, filename=file_name),
            caption=LEXICON_RU.get("transcribed_document_caption"),
        )
        await progress_bar.stop(chat_id=transcribed_text_data.telegram_message.from_user.id)
        process_queue.transcribed_text_sender_queue.task_done()
    predicted_duration_for_summary = await estimate_gen_summary_duration(text=transcribed_text_data.transcribed_text)
    await progress_bar.start(
        chat_id=transcribed_text_data.telegram_message.from_user.id,
        time=predicted_duration_for_summary,
        process_name="написание саммари",
    )
    result: PipelineData = await process_queue.result_dispatching_queue.get()
    process_queue.result_dispatching_queue.task_done()
    if result.summary_text:
        await progress_bar.stop(chat_id=result.telegram_message.from_user.id)
        await user_repository.delete_one_attempt(tg_id=result.telegram_message.from_user.id)
        await bot.send_message(chat_id=result.telegram_message.chat.id, text=result.summary_text)

        await user_balance_repo.update_time_balance(
            tg_id=result.telegram_message.from_user.id,
            time_to_subtract=result.file_duration,
        )

        time_left = await user_balance_repo.get_user_time_balance(tg_id=result.telegram_message.from_user.id)
        await bot.send_message(
            chat_id=result.telegram_message.chat.id,
            text=f"<b>Осталось минут: {await seconds_to_min_sec(time_left)}</b>\n\n{LEXICON_RU['next']}",
            reply_markup=crete_inline_keyboard_assistants(
                assistant_repository,
                user_tg_id=result.telegram_message.from_user.id,
            ),
        )

        whisper_cost = await calculate_whisper_cost(duration_sec=result.file_duration)
        gpt_cost = await calculate_gpt_cost_with_tiktoken(
            input_text=result.transcribed_text,
            response_text=result.summary_text,
            model=await GPTModelManager().get_current_gpt_model_in_use_from_env(),
        )

        meta_information = {
            "ai_model": {
                "summary_model": env("MODEL_VERSION"),
                "transcribe_model": env("WHISPER_MODEL_VERSION"),
            },
            "costs": {
                "whisper": whisper_cost,
                "gpt": gpt_cost,
                "total": round(float(whisper_cost + gpt_cost), 2),
            },
            "file_info": {
                "file_duration": result.file_duration,
                "file_type": result.file_type,
            },
            "process_info": {
                "time_by_stages": result.process_time,
                "total_time": sum([stage["total_time"] for stage in result.process_time.values()]),
            },
        }

        await document_repository.add_meta_information(
            tg_id=result.telegram_message.from_user.id,
            doc_id=result.debase_document_id,
            info=meta_information,
        )
        await state.clear()
