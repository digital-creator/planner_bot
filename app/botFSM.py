from aiogram.dispatcher.filters.state import State, StatesGroup


class PlannerStates(StatesGroup):
    set_task_state_0 = State()
    set_day = State()
    change_month = State()
    change_year = State()
    change_year_cleaner = State()
    recall_task = State()
    get_task_state_0 = State()
    get_task_choice_date = State()
    task_view = State()
