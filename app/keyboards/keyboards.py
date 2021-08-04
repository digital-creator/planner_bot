from aiogram.types import InlineKeyboardMarkup,\
 InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.bot_utils import utils
import calendar


class BotKeyboards():

    names_months = list(
                    ("Январь", "Февраль", "Март", "Апрель",
                    "Май", "Июнь", "Июль", "Август",
                    "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",)
                    )
    name_days = (
                InlineKeyboardButton("Пн", callback_data='.'),
                InlineKeyboardButton("Вт", callback_data='.'),
                InlineKeyboardButton("Ср", callback_data='.'),
                InlineKeyboardButton("Чт", callback_data='.'),
                InlineKeyboardButton("Пт", callback_data='.'),
                InlineKeyboardButton("Сб", callback_data='.'),
                InlineKeyboardButton("Вс", callback_data='.')
                )

    def start_kb(self):
        kb = InlineKeyboardMarkup(row_width=1)
        array_button = [
            InlineKeyboardButton("Добавить задачу", callback_data='set_task'),
            InlineKeyboardButton("Посмотреть задачи", callback_data='get_task')
                       ]
        for button in array_button:
            kb.insert(button)
        return kb

    def calendar_tasks(
        self, year, month: int, end_day: int = 0, active_days: list = None, state=None,
        ):
        name_month = None
        if isinstance(month, str):
            name_month = month
            month = self.names_months.index(month) + 1
        else:
            name_month = self.names_months[month - 1]
        ct = calendar.Calendar()
        calendar_tasks = InlineKeyboardMarkup()

        days = list()
        calendar_tasks.row(InlineKeyboardButton(
                              text=name_month,
                              switch_inline_query_current_chat='Сменить месяц'
                                ),
                            InlineKeyboardButton(
                              text=year,
                              callback_data='change_year')
                                )
        calendar_tasks.row(
                            self.name_days[0], self.name_days[1],
                            self.name_days[2], self.name_days[3],
                            self.name_days[4], self.name_days[5],
                            self.name_days[6]
                          )
        for week in ct.monthdayscalendar(year, month):
            for day in week:
                if day == 0 or (day > end_day and end_day > 0):
                    day = ' '
                if state == 'get' and day != ' ':
                    if f'{day}_{month}' in active_days:
                        date = utils.create_datetime(day, month, year)
                        inline_button = InlineKeyboardButton(
                            str(day),
                            switch_inline_query_current_chat=str(date)
                        )
                    else:
                        inline_button = InlineKeyboardButton(
                            str(day),
                            callback_data='_')

                else:
                    inline_button = InlineKeyboardButton(
                        str(day), callback_data=f'{day}_{month}_{year}'
                                                        )
                days.append(inline_button)
            calendar_tasks.row(
                                days[0], days[1], days[2], days[3],
                                days[4], days[5], days[6]
                               )
            days.clear()

        return calendar_tasks

    def complete_set_task(self):
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton('Добавить ещё задачу', callback_data='next_set'),
            InlineKeyboardButton('В Меню', callback_data='menu'))
        kb.insert(
            InlineKeyboardButton('Напомни мне о задаче', callback_data='recall'))
        return kb

    def state_task(self):
        return InlineKeyboardMarkup(row_width=2).row(
            InlineKeyboardButton('Я выполнил', callback_data='task_complete'),
            InlineKeyboardButton('Я не выполнил', callback_data='task_dnt_complete')
        ).insert(InlineKeyboardButton('Удалить задачу', callback_data='del_task'))

    def after_view_task(self):
        return InlineKeyboardMarkup().row(
            InlineKeyboardButton('В меню', callback_data='menu'),
            InlineKeyboardButton('Я ещё посмотрю задачи', callback_data='not_menu')
        )
    def thanks_recall(self):
        return InlineKeyboardMarkup().row(
            InlineKeyboardButton('Спасибо!', callback_data='thanks')
        )
