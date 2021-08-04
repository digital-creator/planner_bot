from app.config import bot_config
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
from app.botFSM import PlannerStates
from app.message.messages import Messages
from app.keyboards.keyboards import BotKeyboards
from app.bot_utils import utils
from data.data_base import BdPlannerTasks
from exceptions.exceptions import DontPlanningPast
import os


TOKEN = os.environ.get('plannerbot_token')

bd = BdPlannerTasks()

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
kb = BotKeyboards()


@dp.message_handler(commands=['start'], state='*')
async def start_bot(message: types.Message, state: FSMContext):
    await message.reply(Messages.start_bot,
                        reply=False,
                        reply_markup=kb.start_kb())
    await state.update_data({'start_message': message.message_id + 1})


@dp.message_handler(state='*', commands=['menu'])
@dp.callback_query_handler(lambda call: call.data == 'menu', state="*")
async def bot_menu(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    print(data_state)
    if isinstance(message, types.CallbackQuery):
        chat_id = message.message.chat.id
        message = message.message
    else:
        chat_id = message.chat.id

    await utils.del_message(data_state, chat_id, bot)
    await state.reset_state()
    await start_bot(message, state)


@dp. callback_query_handler(lambda call: call.data == 'thanks', state = "*")
async def thanks(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, "Всегда пожалуйста!")
    await bot.delete_message(
        callback_query.from_user.id,
        callback_query.message.message_id
        )


@dp.callback_query_handler(
    (lambda call: call.data == 'set_task' or call.data == 'next_set'),
    state='*')
async def set_task(callback_query: types.callback_query, state: FSMContext):
    chat_id = callback_query.message.chat.id
    if callback_query.data == 'next_set':
        data_states = await state.get_data()
        print(data_states)
        await bot.delete_message(chat_id, data_states['msg_task_complete'])
        await state.reset_data()
    await bot.answer_callback_query(callback_query.id)
    month = callback_query.message.date.month
    year = callback_query.message.date.year
    await PlannerStates.set_task_state_0.set()
    await bot.send_message(
                            chat_id, Messages.set_task_0,
                            reply_markup=kb.calendar_tasks(year, month))
    message_id = callback_query.message.message_id + 1
    await state.update_data({
                            'calendar_id': message_id,
                            'year_now': str(year)
                            })


@dp.inline_handler(state=PlannerStates.set_task_state_0)
async def choice_month(inline_query: types.InlineQuery, state: FSMContext):
    inline_id = inline_query.id
    months_list = kb.names_months
    result_list = list()
    for i, month in enumerate(months_list):
        inline_row = types.InlineQueryResultArticle(
                        id=i, title=month,
                        input_message_content=(
                            types.InputMessageContent(message_text=month)))
        result_list.append(inline_row)
    await bot.answer_inline_query(inline_id, result_list, cache_time=0)
    await PlannerStates.change_month.set()


@dp.message_handler(state=PlannerStates.change_month)
async def change_month(message: types.Message, state: FSMContext):
    name_month = message.text
    del_name_month = message.message_id
    chat_id = message.chat.id
    states_data = await state.get_data()
    calendar_id = states_data['calendar_id']
    year = message.date.year
    calendar = kb.calendar_tasks(year, name_month)
    print(calendar_id)

    await bot.edit_message_reply_markup(
        chat_id, calendar_id, reply_markup=calendar)
    await bot.delete_message(chat_id, del_name_month)
    await PlannerStates.set_task_state_0.set()


@dp.callback_query_handler(
    lambda call: call.data == 'change_year',
    state=PlannerStates.set_task_state_0
)
async def change_year_step_0(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, Messages.set_task_change_year)
    await PlannerStates.change_year.set()


@dp.message_handler(state=PlannerStates.change_year)
async def set_year_changed(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    chat_id = message.chat.id
    try:
        if data_state['msg_year'] is None:
            await state.update_data({'before_msg_year': message.message_id - 1})
        else:
            await utils.del_message(data_state['msg_year'], chat_id, bot)
    except KeyError:
        await state.update_data({'before_msg_year': message.message_id - 1})
    month = message.date.month
    year = message.text.strip()
    year_now_set = data_state['year_now']
    calendar_msg_id = data_state['calendar_id']
    calendar = None
    temp_buffer = dict()
    temp_buffer['msg_year'] = message.message_id
    if year == year_now_set:
        await message.reply(Messages.set_task_identical_year, reply=False)
        temp_buffer['msg_after_year'] = message.message_id + 1
    elif year.isdigit() and len(year) == 4:
        calendar = kb.calendar_tasks(int(year), month,)
        await bot.edit_message_reply_markup(chat_id,
                                            calendar_msg_id,
                                            reply_markup=calendar
                                            )
        temp_buffer['before_msg_year'] = data_state['before_msg_year']
        await utils.del_message(temp_buffer, chat_id, bot)
        await state.update_data({
                                'before_msg_year': None,
                                'msg_year': None,
                                'year_now': year})
        await PlannerStates.set_task_state_0.set()
        return
    else:
        temp_buffer['msg_after_year'] = message.message_id + 1
        await message.reply(Messages.set_task_uncorrect_year,
                            reply=False)
    await state.update_data({'msg_year': temp_buffer})
    return


@dp.callback_query_handler(lambda call: '_' in call.data, state=(
                                                PlannerStates.set_task_state_0)
                                                )
async def print_data(callback_query: types.callback_query, state: FSMContext):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    data_states = await state.get_data()
    if data[0].isdigit():
        day, month, year = data.split('_')
        datetime = None
        try:
            utils.day_is_passed(int(year), int(month), int(day))
            datetime = utils.create_datetime(day, month)
            await bot.send_message(chat_id, Messages.set_task_day)
            await state.update_data({
                                    'calendar_id': data_states['calendar_id'],
                                    'datetime_task': datetime})
            await PlannerStates.set_day.set()
        except DontPlanningPast:
            if callback_query.message.text in kb.names_months:
                pass
            else:
                await bot.answer_callback_query(
                    callback_query.id,
                    Messages.set_task_dont_planning_past,
                    )
            await PlannerStates.set_task_state_0.set()
    else:
        await bot.send_message(chat_id, Messages.set_task_null_day)


@dp.message_handler(state=PlannerStates.set_day)
async def set_day(message: types.Message, state: FSMContext):
    task = message.text
    bot_message = message.message_id - 1
    await state.update_data({
                            'bot_message_id': bot_message,
                            'message_set_day': message.message_id,
                            'task_name': task
                            })
    data_state = await state.get_data()
    datetime = data_state.pop('datetime_task')
    user_id = message.from_user.id
    tasks_dublicated = await bd.get_tasks(user_id, datetime, task)
    if len(tasks_dublicated) == 0:
        await bd.set_data(user_id, datetime, task)
        await message.reply(Messages.set_task_complete,
                            reply=False,
                            reply_markup=kb.complete_set_task())
        await state.update_data({'msg_task_complete': message.message_id + 1})
    else:
        await message.reply(Messages.set_task_duplicate, reply=False)


@dp.callback_query_handler(
    lambda call: call.data == 'recall', state=PlannerStates.set_day)
async def task_recall(callback_query: types.CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    chat_id = callback_query.from_user.id
    date_task = data_state['datetime_task'].split('-')
    year = int(date_task[0])
    month = int(date_task[1])
    end_day = int(date_task[2])
    message_recall_calendar = callback_query.message.message_id + 1
    await bot.send_message(
        chat_id,
        'Когда напомнить?',
        reply_markup=kb.calendar_tasks(year, month, end_day))
    await state.update_data({'message_recall_calendar': message_recall_calendar})
    await PlannerStates.recall_task.set()


@dp.callback_query_handler(state=PlannerStates.recall_task)
async def set_time(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    date = callback_query.data
    await bot.send_message(chat_id, Messages.time_to_recall)
    await state.update_data({'date_to_recall': date})


@dp.message_handler(state=PlannerStates.recall_task)
async def set_time_to_recall(message: types.Message, state: FSMContext):
    message_id = message.message_id
    time_to_recall = message.text
    user_id = message.from_user.id
    data_state = await state.get_data()
    day, month, year = data_state['date_to_recall'].split('_')
    task_name = data_state['task_name']
    datetime_task = data_state['datetime_task']
    msg_buffer = dict()
    msg_buffer['msg_recall'] = [
                                message_id - 1,
                                message_id,
                                message_id + 1
                                ]
    try:
        hour, minute = time_to_recall.split(' ')
        if int(hour) <= 24 and int(minute) <= 60:
            datetime = utils.create_datetime(day, month, year, hour, minute)
            print(datetime)
            await bot.send_message(
                user_id,
                (Messages.recall_complete
                 + f"{task_name}"
                 + ' запланированной на '
                 + datetime_task),
                reply_markup=kb.complete_set_task())
            await state.update_data({'msg_recall': msg_buffer['msg_recall']})
            await bd.update_recall(user_id, datetime, task_name)
            await utils.timer_to_recall(
                user_id, datetime, bot, bd, kb.thanks_recall()
                )
    except Exception as E:
        print(E)
        await bot.send_message(user_id, Messages.uncorrect_time_to_recall)
        await utils.del_message(msg_buffer, user_id, bot, 1)


@dp.callback_query_handler(lambda call: call.data == 'get_task', state='*')
async def get_task(callback_query: types.CallbackQuery, state: FSMContext):
    get_task_calendar_id = callback_query.message.message_id + 1
    await state.update_data({'get_task_calendar_id': get_task_calendar_id})
    chat_id = callback_query.message.chat.id
    year = callback_query.message.date.year
    month = callback_query.message.date.month
    user_id = callback_query.from_user.id
    list_datetime_tasks = await bd.get_list_date(user_id)
    active_days = tuple(f'{date[0].day}_{date[0].month}' for date in list_datetime_tasks)
    calendar = kb.calendar_tasks(year, month, active_days=active_days, state='get')
    await bot.send_message(chat_id, Messages.get_task, reply_markup=calendar)
    await PlannerStates.get_task_choice_date.set()


@dp.callback_query_handler(state=PlannerStates.get_task_choice_date)
async def choice_date(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, Messages.set_task_null_day)


@dp.inline_handler(state=PlannerStates.get_task_choice_date)
async def view_list_tasks(inline_query: types.InlineQuery):
    inline_query_id = inline_query.id
    query_with_date = inline_query.query
    user_id = inline_query.from_user.id
    list_tasks = await bd.get_tasks(user_id, query_with_date)
    inline_list = list()
    dict_preview = dict()
    preview_array = await bd.get_icon_task()
    for complete, url in preview_array:
        dict_preview[str(complete)] = url
    for i, task in enumerate(list_tasks):
        preview = dict_preview[str(task[1])]
        inline_row = types.InlineQueryResultArticle(
            id=str(i),
            title=task[0],
            input_message_content=types.InputMessageContent(
                message_text=task[0]),
            thumb_url=preview,
            thumb_width=5,
            thumb_height=5,
            )
        inline_list.append(inline_row)
    await bot.answer_inline_query(inline_query_id, inline_list, cache_time=0)


@dp.message_handler(state=PlannerStates.get_task_choice_date)
async def task_view(message: types.Message, state: FSMContext):
    await message.reply(Messages.get_task_how, reply=False, reply_markup=kb.state_task())
    await state.update_data({'task_view_del': [
                            message.message_id,
                            message.message_id + 1,
                            message.message_id + 2]})
    await PlannerStates.task_view.set()


@dp.callback_query_handler(
    lambda call: call.data == 'task_complete' or call.data == 'task_dnt_complete',
    state=PlannerStates.task_view)
async def task_state(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if callback_query.data == 'task_complete':
        await bd.update_complete(user_id, True)
        await bot.send_message(
            user_id,
            Messages.get_task_complete,
            reply_markup=kb.after_view_task())
    else:
        await bd.update_complete(user_id, False)
        await bot.send_message(
            user_id,
            Messages.get_task_dont_complete,
            reply_markup=kb.after_view_task())


@dp.callback_query_handler(
    lambda call: call.data == 'not_menu', state=PlannerStates.task_view)
async def not_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await PlannerStates.get_task_choice_date.set()
    chat_id = callback_query.from_user.id
    await bot.send_message(chat_id, 'Хорошо!')
    task_view_data = await state.get_data()
    good_msg = len(task_view_data['task_view_del']) - 1

    for i, message_id in enumerate(task_view_data['task_view_del']):
        await bot.delete_message(chat_id, message_id)
        if i == good_msg:
            await utils.del_message(
                {'last_msg': message_id + 1},
                chat_id,
                bot,
                5)


@dp.message_handler(state='*', content_types=types.ContentTypes.STICKER)
async def photo_id(message: types.Message):
    sticker = message.sticker.file_id
    thumb = message.sticker.thumb.file_id
    await message.reply(sticker + '\n' + thumb, reply=False)
    await bot.send_sticker(message.chat.id, sticker)

# TODO: Добавить функцию удаления задачи
