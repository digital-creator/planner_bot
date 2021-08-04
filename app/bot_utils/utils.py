import datetime as dt
from exceptions.exceptions import DontPlanningPast
import asyncio
import emoji


def create_datetime(day, month, year=None, hour=None, minute=None):
    if year is None:
        year = dt.date.today().year
    if hour is None and minute is None:
        object_date = dt.date(int(year), int(month), int(day))
        date = object_date.strftime('%Y-%m-%d')
        return date
    else:
        object_datetime = dt.datetime(
            int(year), int(month), int(day), int(hour), int(minute))
        datetime = object_datetime.strftime('%Y-%m-%d %H:%M')
        return datetime


async def del_message(data_state: dict, chat_id, bot, timer=0):
    async def wrapper(*args):

        for key_state in data_state.keys():
            if len(key_state) == 0:
                return
            if isinstance(data_state[key_state], int):
                await bot.delete_message(chat_id, data_state[key_state])
            elif isinstance(data_state[key_state], list):
                for i in data_state[key_state]:
                    await bot.delete_message(chat_id, i)

    await asyncio.sleep(timer)
    await wrapper()


def day_is_passed(year: int, month: int, day: int):
    date = dt.date(year, month, day)
    today = dt.date.today()
    timedelta = date - today
    if int(timedelta.days) < 0:
        raise DontPlanningPast('Timedelta Is Zero')
    return


async def timer_to_recall(user_id, recall_datetime, bot, bd, kb):
    recall = dt.datetime.strptime(recall_datetime, '%Y-%m-%d %H:%M')
    seconds_to_recall = (recall - dt.datetime.now()).seconds
    await asyncio.sleep(seconds_to_recall)
    recall_tasks = await bd.get_task_on_recall(user_id, recall_datetime)
    print(recall_tasks)
    name_task = recall_tasks[0][0]
    date = str(recall_tasks[0][1])
    recall = emoji.emojize(
        f'Привет, у тебя на {date} запланировано:\n{name_task}:blush:',
        use_aliases=True
        )
    await bot.send_message(user_id, recall, reply_markup=kb)
