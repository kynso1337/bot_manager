from aiogram.fsm.state import State, StatesGroup

class aForm(StatesGroup):
    add_point = State()
    del_point = State()

    topic_id = State()
    topic_name = State()

    new_link = State()