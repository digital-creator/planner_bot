from aiogram import executor
import Bot


if "__main__" == __name__:
    executor.start_polling(
        Bot.dp,
        timeout=20,
        skip_updates=True,)
