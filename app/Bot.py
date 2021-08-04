from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from message.messages import Messages
from config import bot_config

TOKEN = bot_config.get_config('bot', 'token')

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

print(Messages.start_bot())

@dp.message_handlers(command=['start'])
async def start_bot(message: types.Message):
    message.reply()
