from aiogram.fsm.state import State, StatesGroup


class FSMSummaryFromAudioScenario(StatesGroup):
    load_file = State()
    get_result = State()
