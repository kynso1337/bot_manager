from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from secrets import token_hex
import asyncio

from handlers import main_handler
from admin_handlers import main_admin, chats
from preload.config import *


import logging
logging.basicConfig(level=logging.INFO, filename="logs/bot.log",filemode="w")



async def main():
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(TOKEN)


    dp.include_router(chats.router)

    dp.include_router(main_handler.router)


    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())



if __name__ == '__main__':
    asyncio.run(main())