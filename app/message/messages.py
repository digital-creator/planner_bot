import emoji


class Messages:
    start_bot = emoji.emojize('Привет! Что хочешь сделать?')
    get_sticker_id = 'Пришли мне стикер, а я тебе отправлю его id'
    set_task_0 = emoji.emojize('Давай выберем день для задачи!')
    set_task_null_day = emoji.emojize(
        'Это пустой день.. Выбери другой :relieved:', use_aliases=True)
    set_task_day = emoji.emojize(
        "Прекрасно! Теперь отправь мне задачу! :relieved:", use_aliases=True)
    set_task_dont_planning_past = emoji.emojize(
        "Увы, прошлое не запланировать! :relieved:", use_aliases=True
    )
    set_task_change_year = 'Отправь мне год за который хочешь увидеть календарь..'
    set_task_complete = emoji.emojize(
        'Задача добавлена! :wink:', use_aliases=True
        )
    set_task_uncorrect_year = emoji.emojize(
        'Я не знаю такой год :scream:\nОтправь мне правильный год , например - 2021',
        use_aliases=True)
    set_task_identical_year = 'Этот год у тебя выбран сейчас..'
    set_task_duplicate = emoji.emojize(
        'В этот день у тебя уже есть такая задача :blush:', use_aliases=True
        )
    time_to_recall = emoji.emojize(
        ('Во сколько часов напомнить тебе о задаче?:slightly_smiling_face:\n' +
        'Отправь мне время через пробел.\nНапример, 06 05'),
        use_aliases=True
    )
    recall_complete = emoji.emojize(
        'Готово!:blush: Я Напомню тебе о задаче:\n'
        ,use_aliases=True)
    uncorrect_time_to_recall = emoji.emojize(
        'Я не понимаю такой формат:scream:\n' +
        'Отправь мне время через пробел. Например, 06 05', use_aliases=True)
    get_task = emoji.emojize(
        'Для какого дня будем смотреть задачи? :blush:', use_aliases=True
        )
    get_task_how = emoji.emojize('Как твои успехи?:blush:', use_aliases=True)
    get_task_complete = emoji.emojize(
        'Хорошая работа!\n+1 к очкам достижений:sunglasses:', use_aliases=True)
    get_task_dont_complete = emoji.emojize(
        'Печально, конечно..:relieved: Но могло быть и хуже!\nНапример, если ты за день не выполнил ни одной задачи:blush:',
        use_aliases=True

    )
