from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_phone = State()


class QueueStates(StatesGroup):
    select_org    = State()  # Ташкилот интихоб
    select_branch = State()  # Шӯъба интихоб
    select_queue  = State()  # Навбат интихоб
    in_queue      = State()  # Навбат гирифта шуд