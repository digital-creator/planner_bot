import datetime as dt
from exceptions.exceptions import DontPlanningPast
from data.data_base import BdPlannerTasks
import asyncio
import emoji

bd = BdPlannerTasks()


def create_datetime(day=None, month=None, year=None,
                    hour=None, minute=None, datetime_now=False):
    if datetime_now:
        return dt.datetime.now()
    elif year is None:
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
    print(recall)
    seconds_to_recall = (recall - dt.datetime.now()).seconds
    print(seconds_to_recall)
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


async def check_active_recall(bot, bd, kb):
    datetime_now = create_datetime(datetime_now=True)
    list_active_recall = await bd.get_active_recall(
        str(datetime_now).split('.')[0]) # Ибо дата будет вида 2021-08-04 11:38:31.373812
    for user_id, recall in list_active_recall:
        recall_datetime = create_datetime(recall.day, recall.month, recall.year,
                                          recall.hour, recall.minute)
        await timer_to_recall(user_id, recall_datetime, bot, bd, kb)
