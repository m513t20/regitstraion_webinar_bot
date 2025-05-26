from aiogram.fsm.state import State,StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    admin_login=State()
    link_send=State()