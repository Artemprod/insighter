from aiogram.fsm.state import State, StatesGroup


class PaymentScenario(StatesGroup):
    waiting_for_payment = State()
