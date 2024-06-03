from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestChat
from preload.config import *


admin_menu = [[KeyboardButton(text = 'Чаты')],
              [KeyboardButton(text = 'Подключить чат', request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False,
                                                                   user_administrator_rights=all_rights,
                                                                   bot_administrator_rights=all_rights))]]
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_menu)
