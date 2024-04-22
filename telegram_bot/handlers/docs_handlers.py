from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from DB.Mongo.mongo_db import UserDocsRepoORM
from analitics.event_enteties import BaseEvent
from analitics.events import EventsNames
from analitics.mixpanel_system.mixpanel_tracker import MixpanelAnalyticsSystem
from lexicon.LEXICON_RU import LEXICON_RU
from telegram_bot.keyboards.calback_factories import DocumentsCallbackFactory
from telegram_bot.keyboards.inline_keyboards import (
    create_inline_keyboard_show_docs,
    crete_inline_keyboard_back_from_docks,
)

router = Router()


class FSMGetMyDocs(StatesGroup):
    get_my_docks = State()
    show_doc = State()


@router.callback_query(F.data == "my_docs")
async def processed_show_my_docks(callback: CallbackQuery, mixpanel_tracker: MixpanelAnalyticsSystem):
    keyboard = await create_inline_keyboard_show_docs(user_tg_id=callback.from_user.id)
    if callback.message.text:
        await callback.message.edit_text(
            text=LEXICON_RU.get("documents_tittle", "как дела ?"),
            reply_markup=keyboard,
        )
        await callback.answer()
    else:
        await callback.message.answer(
            text=LEXICON_RU.get("documents_tittle", "как дела ?"),
            reply_markup=keyboard,
        )
        await callback.answer()
    mixpanel_tracker.send_event(
        event=BaseEvent(user_id=callback.from_user.id, event_name=EventsNames.VIEWED_HISTORY.value))


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой


@router.callback_query(F.data.startswith("page_"))
async def process_page_change(callback: CallbackQuery, document_repository: UserDocsRepoORM):
    page_num = int(callback.data.split("_")[1])
    user_tg_id = callback.from_user.id

    # Обновить страницу пользователя с помощью статического метода
    await document_repository.update_user_page(tg_id=user_tg_id, current_page=page_num)

    new_markup = await create_inline_keyboard_show_docs(user_tg_id, current_page=page_num)
    await callback.message.edit_reply_markup(reply_markup=new_markup)
    await callback.answer()


@router.callback_query(DocumentsCallbackFactory.filter())
async def processed_chose_dock(
    callback: CallbackQuery,
    callback_data: DocumentsCallbackFactory,
    state: FSMContext,
    document_repository: UserDocsRepoORM,
):
    document = await document_repository.get_doc_by_date(tg_id=callback.from_user.id, date=callback_data.document_date)
    back_keyboard = crete_inline_keyboard_back_from_docks()
    msg = f"""
<b>Текст документа</b>\n\n
<b>Трансрибация</b> ( часть текста ):{document.get('transcription', 'Нету транскрипции')[:600]} <b>...</b>\n\n
<b>Саммари</b>: :{document.get('summary', 'Нету саммари')}
    """
    await callback.message.edit_text(text=f"{msg}", reply_markup=back_keyboard)
    await callback.answer()
