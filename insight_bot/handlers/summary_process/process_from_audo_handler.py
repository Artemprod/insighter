import os

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.types import ContentType

from api.progress_bar.command import ProgressBarClient
from DB.Mongo.mongo_db import MongoAssistantRepositoryORM, MongoUserRepoORM, UserDocsRepoORM
from api.gpt import GPTAPIrequest
from api.media_recognition.recognition import MediaRecognition
from keyboards.calback_factories import AssistantCallbackFactory
from keyboards.inline_keyboards import crete_inline_keyboard_assistants, \
    crete_inline_keyboard_back_from_loading
from lexicon.LEXICON_RU import LEXICON_RU
from services.service_functions import get_media_file, load_assistant, \
    generate_text_file, form_content, estimate_transcribe_duration, estimate_gen_summary_duration
from states.summary_from_audio import FSMSummaryFromAudioScenario

# Повесить мидлварь только на этот роутер
router = Router()


@router.callback_query(AssistantCallbackFactory.filter())
async def processed_gen_answer(callback: CallbackQuery,
                               callback_data: AssistantCallbackFactory,
                               state: FSMContext
                               ):
    # Проверяем, есть ли текст в сообщении
    if callback.message.text:
        message = await callback.message.edit_text(
            text=LEXICON_RU.get('instructions', 'как дела ?'),
            reply_markup=crete_inline_keyboard_back_from_loading())

    else:
        message = await callback.message.answer(
            text=LEXICON_RU.get('instructions', 'как дела ?'),
            reply_markup=crete_inline_keyboard_back_from_loading())


    await state.update_data(assistant_id=callback_data.assistant_id,
                            instruction_message_id=message.message_id)
    await state.set_state(FSMSummaryFromAudioScenario.do_recognition)
    await callback.answer()


@router.message(FSMSummaryFromAudioScenario.do_recognition, F.content_type.in_({ContentType.VOICE,
                                                                                ContentType.AUDIO,
                                                                                }))
async def processed_do_recognition(message: Message, bot: Bot,

                                   media_recognition: MediaRecognition,

                                   state: FSMContext, assistant_repo: MongoAssistantRepositoryORM,
                                   user_repo: MongoUserRepoORM, doc_repo: UserDocsRepoORM,
                                   assistant: GPTAPIrequest, progress_bar: ProgressBarClient,):
    async def transcribe_and_save(media_recognition, chat_id, doc_repo, doc_id, duration):
        await progress_bar.start(chat_id=message.from_user.id, time=duration, process_name='распознавание аудио')
        file_on_disk = await get_media_file(data_from_income_message=message,
                                            bot=bot, container_id='insighter-telegram_bot_server-1')
        recognized_text = await media_recognition.transcribe_file(file_on_disk)
        await doc_repo.save_new_transcribed_text(tg_id=chat_id, doc_id=doc_id, transcribed_text=recognized_text)
        if recognized_text:
            os.remove(file_on_disk)
            await progress_bar.stop(chat_id=message.from_user.id)
            return recognized_text

    data = await state.get_data()
    instruction_message_id = int(data.get('instruction_message_id'))
    audio = message.audio
    if instruction_message_id:
        await bot.delete_message(chat_id=message.chat.id, message_id=instruction_message_id)
    progres_bar_time = await estimate_transcribe_duration(audio=audio)
    doc_id = await doc_repo.create_new_doc(tg_id=message.from_user.id)
    await transcribe_and_save(media_recognition=media_recognition, chat_id=message.from_user.id
                              , doc_repo=doc_repo, doc_id=doc_id, duration=progres_bar_time)
    await state.update_data(doc_id=doc_id)
    await state.set_state(FSMSummaryFromAudioScenario.do_ai_conversation)
    await processed_do_ai_conversation(message=message, state=state,
                                       user_repo=user_repo, assistant=assistant, bot=bot,
                                       assistant_repo=assistant_repo,
                                       doc_repo=doc_repo, progress_bar=progress_bar)



@router.message(FSMSummaryFromAudioScenario.do_recognition)
async def processed_do_ai_conversation(message: Message, bot: Bot,
                                       state: FSMContext, assistant_repo: MongoAssistantRepositoryORM,
                                       user_repo: MongoUserRepoORM, doc_repo: UserDocsRepoORM,
                                       assistant: GPTAPIrequest, progress_bar: ProgressBarClient):
    data = await state.get_data()

    # TODO Вынеси все это в сервес
    # Саммари
    # Загрузить асистента

    async def make_summary(message: Message, bot: Bot,
                           state: FSMContext, assistant_repo: MongoAssistantRepositoryORM,
                           doc_repo: UserDocsRepoORM,
                           assistant: GPTAPIrequest, predicted_duration, recognized_text):
        await progress_bar.start(chat_id=message.from_user.id, time=predicted_duration, process_name="написание саммари")
        work_assistant = await load_assistant(state=state, Gpt_assistant=assistant, assistant_repo=assistant_repo)
        summary = await work_assistant.conversation(recognized_text)
        await message.answer(text=summary)
        await doc_repo.save_new_summary_text(tg_id=message.from_user.id, doc_id=data.get('doc_id'),
                                             summary_text=summary)
        content = await form_content(summary=summary, transcribed_text=recognized_text)
        if summary:
            await progress_bar.stop(chat_id=message.from_user.id)
            file_in_memory, file_name = await generate_text_file(content=content, message_event=message)
            await bot.send_document(chat_id=message.from_user.id,
                                    document=BufferedInputFile(file=file_in_memory, filename=file_name),
                                    )

    attempts = await user_repo.get_user_attempts(tg_id=message.from_user.id)
    recognized_text = await doc_repo.load_transcribed_text(tg_id=message.from_user.id, doc_id=data.get('doc_id'))
    predicted_duration = await estimate_gen_summary_duration(count_tokens=assistant.num_tokens_from_string,
                                                             text=recognized_text)

    await make_summary(message=message, assistant_repo=assistant_repo,
                       doc_repo=doc_repo,
                       assistant=assistant, bot=bot, state=state, predicted_duration=predicted_duration,
                       recognized_text=recognized_text)

    await message.answer(text=f"<b>Осталось запросов: {attempts}</b>  \n\n {LEXICON_RU['next']}", reply_markup=crete_inline_keyboard_assistants(assistant_repo,
                                                                                                user_tg_id=message.from_user.id))
    await user_repo.delete_one_attempt(tg_id=message.from_user.id)
    await state.clear()
