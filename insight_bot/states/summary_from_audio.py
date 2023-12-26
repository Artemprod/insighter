from aiogram.fsm.state import StatesGroup, State


class FSMSummaryFromAudioScenario(StatesGroup):
    do_recognition = State()
    do_ai_conversation = State()