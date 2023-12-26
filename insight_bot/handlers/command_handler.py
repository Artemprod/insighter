from aiogram.filters import CommandStart,Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from DB.Mongo.mongo_db import MongoAssistantRepositoryORM, MongoUserRepoORM

from keyboards.inline_keyboards import crete_inline_keyboard_assistants, crete_inline_keyboard_back_from_loading

from lexicon.LEXICON_RU import LEXICON_RU

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, assistant_repo: MongoAssistantRepositoryORM,
                                user_repo: MongoUserRepoORM):
    if not await user_repo.check_user_in_db(tg_id=message.from_user.id):
        await user_repo.save_new_user(
            tg_username=message.from_user.username,
            name=message.from_user.first_name,
            tg_id=message.from_user.id,
        )
    attempts = await user_repo.get_user_attempts(tg_id=message.from_user.id)
    assistant_keyboard = crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id)
    print()
    await message.answer(text=f"{LEXICON_RU['description']}\n\n <b>Осталось запросов: {attempts}</b> \n\n{LEXICON_RU['next']} ", reply_markup=assistant_keyboard)

# @router.message(Command(commands=['help']))
# async def process_start_command(message: Message, assistant_repo: MongoAssistantRepositoryORM,
#                                 user_repo: MongoUserRepoORM):
#     if message.text:
#         await message.edit_text(
#             text=LEXICON_RU.get('help', 'как дела ?'),
#             reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))
#
#     else:
#         await message.answer(
#             text=LEXICON_RU.get('help', 'как дела ?'),
#             reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))

@router.message(Command(commands=['feedback']))
async def process_start_command(message: Message, assistant_repo: MongoAssistantRepositoryORM,
                                user_repo: MongoUserRepoORM):
    if message.text:
        await message.edit_text(
            text=LEXICON_RU.get('help', 'как дела ?'),
            reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))

    else:
        await message.answer(
            text=LEXICON_RU.get('help', 'как дела ?'),
            reply_markup=crete_inline_keyboard_assistants(assistant_repo, user_tg_id=message.from_user.id))

@router.callback_query(F.data == "payed")
async def process_payed(callback: CallbackQuery, assistant_repo: MongoAssistantRepositoryORM,
                        user_repo: MongoUserRepoORM):
    attempts = await user_repo.get_user_attempts(tg_id=callback.from_user.id)
    assistant_keyboard = crete_inline_keyboard_assistants(assistant_repo, user_tg_id=callback.from_user.id)
    if callback.message.text:
        await callback.message.edit_text(text=f"<b> Осталось запросов: {attempts}</b>  \n\n {LEXICON_RU['next']}", reply_markup=assistant_keyboard)
        await callback.answer()
    else:
        await callback.message.answer(text=f"<b>Осталось запросов: {attempts}</b>  \n\n {LEXICON_RU['next']}", reply_markup=assistant_keyboard)
        await callback.answer()


@router.callback_query(F.data == "base")
async def process_payed(callback: CallbackQuery, assistant_repo: MongoAssistantRepositoryORM,
                        user_repo: MongoUserRepoORM):
    attempts = await user_repo.get_user_attempts(tg_id=callback.from_user.id)
    assistant_keyboard = crete_inline_keyboard_assistants(assistant_repo, user_tg_id=callback.from_user.id)
    if callback.message.text:
        await callback.message.edit_text(text=f"<b>Осталось запросов: {attempts}</b>  \n\n {LEXICON_RU['next']}", reply_markup=assistant_keyboard)
    else:
        await callback.message.answer(text=f"<b>Осталось запросов:{attempts}</b>  \n\n {LEXICON_RU['next']}", reply_markup=assistant_keyboard)
