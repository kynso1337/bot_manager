from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ChatShared

from secrets import token_hex
from datetime import datetime
import pytz

from preload import functions
from preload.databases import *
from preload.config import *
from preload.states import *
from preload.keyboard import *
from preload.functions import *


router = Router()
bot = Bot(TOKEN)


import logging
logging.basicConfig(level=logging.INFO, filename="logs/handlers.log",filemode="w")



