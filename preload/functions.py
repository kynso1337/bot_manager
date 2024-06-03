import json

from preload.databases import *
from preload.config import *
from preload.states import *
from preload.keyboard import *

from aiogram import Bot
from aiogram.types import FSInputFile
from secrets import token_hex
from aiogram.types.switch_inline_query_chosen_chat import SwitchInlineQueryChosenChat

bot = Bot(TOKEN)


async def generateChats():
    kbs = []
    select = cur.execute('select * from data').fetchall()
    for row in select:
        info = json.loads(row[1])
        kbs.append([InlineKeyboardButton(text = info['title'], callback_data=f'select_chat_{row[0]}')])
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    return '''<b>Здесь ты можешь управлять подключёнными чатами.</b>
    
• Изменять шаблоны для них
• Удалять чаты''', kbs


async def generateOneChat(chat_id):
    select = cur.execute('select * from data where id == ?', (chat_id, )).fetchone()
    info = json.loads(select[1])
    settings = json.loads(select[2])
    topics = cur3.execute('select * from data where chat == ?', (chat_id, )).fetchall()
    kbs = []
    for row in topics:
        kbs.append([InlineKeyboardButton(text = row[2], callback_data=f'select_topic_{chat_id}_{row[1]}')])
    kbs.append([InlineKeyboardButton(text = '➕ Добавить топик', callback_data=f'add_topic_{chat_id}')])
    kbs.append([InlineKeyboardButton(text = '🗑 Удалить', callback_data=f'delete_chat_{chat_id}')])
    kbs.append([InlineKeyboardButton(text = '← Назад', callback_data='back_to_allchannels')])

    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)

    text = '\n'.join(settings)
    return f'''Чат <b><a href="{info["link"]}">{info["title"]}</a></b>
id чата: <code>{chat_id}</code>

<b>Текущий шаблон:</b>
{text if text != '' else 'не установлен'}''', kbs


async def generateTopic(chat_id, topic_id):
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    name = select[2]
    settings = json.loads(select[3])
    chat_select = cur.execute('select * from data where id == ?', (chat_id,)).fetchone()
    info = json.loads(chat_select[1])
    text = '\n'.join(settings['points'])
    kbs = [[InlineKeyboardButton(text = 'Настроить пункты', callback_data=f'pattern_settings_{chat_id}_{topic_id}')],
           [InlineKeyboardButton(text = 'Изменить ссылку', callback_data=f'edit_link_{chat_id}_{topic_id}')],
           [InlineKeyboardButton(text = '🗑 Удалить', callback_data=f'delete_topic_{chat_id}_{topic_id}')],
           [InlineKeyboardButton(text = '← Назад', callback_data=f'select_chat_{chat_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    return f'''Топик <b><a href="https://t.me/c/{str(chat_id).replace("-100", "")}/{topic_id}">"{name}"</a></b>
Предустановленная ссылка: {settings["link"] if settings['link'] != '' else 'не установлена'}

<b>Текущий шаблон:</b>
{text if text != '' else 'не установлен'}''', kbs


#chat integer, topic integer, name text, settings text
async def generatePatternSettings(chat_id, topic_id):
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    settings = settings['points']
    text = '\n'.join(f'{i+1}. {set}' for i, set in enumerate(settings))

    kbs = [[InlineKeyboardButton(text = 'Добавить пункт', callback_data=f'add_point_{chat_id}_{topic_id}')],
           [InlineKeyboardButton(text = 'Удалить пункт', callback_data=f'delete_point_{chat_id}_{topic_id}')],
           [InlineKeyboardButton(text = '← Назад', callback_data=f'select_topic_{chat_id}_{topic_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)

    return f'''<b>Текущий шаблон:</b>
{text if text != '' else 'не установлен'}''', kbs

#id integer, chat integer, topic integer, message text, links text
async def generateLinks(chat, topic):
    links_list = []
    select = cur2.execute('select * from data where chat == ? and topic == ?', (chat, topic)).fetchall()
    for row in select:
        links = json.loads(row[4])
        for l in links:
            links_list.append({'link': l, 'chat_id': row[1], 'message_id': row[0]})
    return links_list

#id integer, info text, settings text
async def checkPatternMessage(chat_id, topic_id, check_text):
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    settings = settings['points']
    settings_dict = {}
    for row in settings:
        settings_dict[row.lower()] = None
    print(list(settings_dict.keys()))

    text = (check_text.lower()).split('\n')
    for row in text:
        for check in list(settings_dict.keys()):
            if not settings_dict[check]:
                if row.find(check) != -1:
                    if row.split(check)[-1] != '' and row.split(check)[-1] != ' ' and row.split(check)[-1] != ' \n' and row.split(check)[-1] != '\n':
                        print(row)
                        settings_dict[check] = True
                    else:
                        settings_dict[check] = False
    text = ''

    print(settings_dict)
    for key in list(settings_dict.keys()):
        if settings_dict[key] == False:
            text += f'• Пункт <b>"{key}"</b> пуст\n'
        elif settings_dict[key] == None:
            text += f'• Отсутствует пункт <b>"{key}"</b>\n'

    return text