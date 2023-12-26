import datetime
import os

import chardet
from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, CallbackQuery, BufferedInputFile
from aiogram.types import ContentType
import aiofiles
from DB.Mongo.mongo_db import MongoAssistantRepositoryORM, MongoUserRepoORM, UserDocsRepoORM
from api.gpt import GPTAPIrequest
from keyboards.calback_factories import AssistantCallbackFactory
from keyboards.inline_keyboards import crete_inline_keyboard_assistants, \
    crete_inline_keyboard_back_from_loading
from lexicon.LEXICON_RU import LEXICON_RU
from services.service_functions import get_media_file, remove_file_async, load_assistant, generate_text_file

router = Router()


class FSMGeneration(StatesGroup):
    gen_answer = State()


@router.callback_query(AssistantCallbackFactory.filter())
async def processed_gen_answer(callback: CallbackQuery,
                               callback_data: AssistantCallbackFactory,
                               state: FSMContext
                               ):
    await state.update_data(assistant_id=callback_data.assistant_id)

    await callback.message.edit_text(
        text=LEXICON_RU.get('instructions', 'как дела ?'), reply_markup=crete_inline_keyboard_back_from_loading())
    await state.set_state(FSMGeneration.gen_answer)
    await callback.answer()


@router.message(FSMGeneration.gen_answer, F.content_type.in_({ContentType.DOCUMENT,
                                                              }))
async def processed_make_answer_from_document(message: Message, bot: Bot
                                              ,
                                              state: FSMContext, assistant_repo: MongoAssistantRepositoryORM,
                                              user_repo: MongoUserRepoORM, doc_repo: UserDocsRepoORM,assistant: GPTAPIrequest):
    data = await state.get_data()
    doc_id = await doc_repo.create_new_doc(tg_id=message.from_user.id)
    work_assistant = await load_assistant(state=state, Gpt_assistant=assistant, assistant_repo=assistant_repo)
    gif_path = os.path.join('media', 'gifs')
    file_on_disk = await get_media_file(data_from_income_message=message,
                                        bot=bot, )

    doc_directory = os.path.join('media', 'recommendations')
    doc_filename = f'{message.from_user.id}_{datetime.datetime.now().strftime("%d_%B_%Y_%H_%M_%S")}.txt'
    doc_path = os.path.join(doc_directory, doc_filename)
    os.makedirs(doc_directory, exist_ok=True)
    sent_waiting_message = await message.edit_text(text="Сейчас будет магия...")
    sent_message = await bot.send_animation(chat_id=message.from_user.id,
                                            animation=FSInputFile(os.path.join(gif_path, 'loading_2.gif')))

    async with aiofiles.open(file_on_disk, 'rb') as rawfile:
        rawdata = await rawfile.read()
        result = chardet.detect(rawdata)
        encoding = result['encoding']

    async with aiofiles.open(file_on_disk, 'r', encoding=encoding) as t:
        # Чтение содержимого файла асинхронно
        content = await t.read()
        answer = await work_assistant.conversation(content)
        await bot.delete_message(chat_id=message.from_user.id, message_id=sent_waiting_message.message_id)
        await message.answer(text=answer)

    await bot.delete_message(chat_id=message.from_user.id, message_id=sent_message.message_id)
    await message.answer(text=LEXICON_RU['your_file'])

    file_in_memory, file_name = await generate_text_file(content=answer, message_event=message)

    await bot.send_document(chat_id=message.from_user.id,
                            document=BufferedInputFile(file=file_in_memory, filename=file_name))
    await state.clear()
    await message.answer(text=LEXICON_RU['next'],
                         reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))
    # TODO Потанцеально могут быть проблемы со снятие

    await user_repo.delete_one_attempt(tg_id=message.from_user.id)
    await doc_repo.save_new_summary_text(tg_id=message.from_user.id, doc_id=doc_id,summary_text=answer)
    await remove_file_async(doc_path)
    await remove_file_async(file_on_disk)


@router.message(FSMGeneration.gen_answer, F.content_type.in_({ContentType.TEXT,
                                                              }))
async def processed_make_answer_from_text(message: Message, bot: Bot,

                                          state: FSMContext, assistant_repo: MongoAssistantRepositoryORM,
                                          user_repo: MongoUserRepoORM, doc_repo: UserDocsRepoORM,assistant: GPTAPIrequest):
    data = await state.get_data()
    doc_id = await doc_repo.create_new_doc(tg_id=message.from_user.id)
    work_assistant = await load_assistant(state=state, Gpt_assistant=assistant, assistant_repo=assistant_repo)
    gif_path = os.path.join('media', 'gifs')

    sent_message = await bot.send_animation(chat_id=message.from_user.id,
                                            animation=FSInputFile(os.path.join(gif_path, 'loading_2.gif')))

    doc_directory = os.path.join('media', 'recommendations')
    doc_filename = f'{message.from_user.id}_{datetime.datetime.now().strftime("%d_%B_%Y_%H_%M_%S")}.txt'
    doc_path = os.path.join(doc_directory, doc_filename)
    os.makedirs(doc_directory, exist_ok=True)
    async with aiofiles.open(doc_path, 'w') as f:  # Используем 'w' для создания файла
        answer = await assistant.conversation(message.text)
        print(answer)
        await f.write(answer + '\n')
        await message.answer(text=answer)
        await bot.delete_message(chat_id=message.from_user.id, message_id=sent_message.message_id)
    await message.answer(text=LEXICON_RU['your_file'])
    await bot.send_document(chat_id=message.from_user.id, document=FSInputFile(doc_path))
    await remove_file_async(doc_path)
    await state.clear()
    await message.answer(text=LEXICON_RU['next'],
                         reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))

    await user_repo.delete_one_attempt(tg_id=message.from_user.id)
    await doc_repo.save_new_summary_text(tg_id=message.from_user.id, doc_id=doc_id, summary_text=answer)