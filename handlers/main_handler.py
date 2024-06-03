import json

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.filters import Command, CommandObject
from aiogram import Router, F, Bot

from secrets import token_hex
from urlextract import URLExtract

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


#id integer, info text, settings text

@router.message(Command(commands=['start']))
async def start_func(message: Message, state: FSMContext, command: CommandObject):
    if message.from_user.id in admin_ids:
        if command.mention == bot_username:
            if len(cur.execute('select * from data where id == ?', (message.chat.id, )).fetchall()) == 0:
                info = {'title': message.chat.title,
                        'link': message.chat.invite_link}
                cur.execute('insert into data values (?, ?, ?)', (message.chat.id, json.dumps(info), '[]'))
                base.commit()
                text, kbs = await generateChats()
                await bot.send_message(message.from_user.id, f'Чат <b>"{message.chat.title}"</b> успешно добавлен!', parse_mode='HTML')
                await bot.send_message(message.from_user.id, text, parse_mode='HTML', reply_markup=kbs)
        else:
            await message.answer(f'👋 <b>Привет, {message.from_user.first_name}!</b>\n\nДобро пожаловать в бота для администрирования чатов.',
                             reply_markup=admin_menu, parse_mode='HTML')
    else:
        await message.answer('Test')

#id integer, chat integer, topic integer, message text, links text
@router.message(F.content_type.in_(any))
async def chatHandFunc(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        if len(cur.execute('select * from data where id == ?', (message.chat.id, )).fetchall()) != 0:
            links_list = await generateLinks(message.chat.id, message.message_thread_id)
            extractor = URLExtract()
            urls = extractor.find_urls(message.html_text)
            new_urls = []
            res = True
            print(urls)
            if len(urls) != 0:
                for l in urls:
                    if l.find('drive.google') == -1 and l.find('disk.yandex') == -1 and l.find('t.me') == -1:
                        new_urls.append(l)
                select = cur3.execute('select * from data where chat == ? and topic == ?',
                                      (message.chat.id, message.message_thread_id)).fetchone()
                print(message.chat.id, message.message_thread_id)
                print(select)
                settings = json.loads(select[3])
                prelink = settings['link']
                if len(new_urls) != 0:
                    print(new_urls)
                    prelink_detect = True
                    for l in new_urls:
                        print(l.find(prelink))
                        if l.find(prelink) == -1:
                            prelink_detect = l
                            break
                    if prelink_detect == True:
                        if res == True:
                            text = message.text if message.text else message.caption if message.caption else ''
                            check = await checkPatternMessage(message.chat.id, message.message_thread_id, text)
                            if check != '':
                                await message.delete()
                                await bot.send_message(message.chat.id,
                                                       f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, обнаружены следующие ошибки в сообщении:\n{check}',
                                                       parse_mode='HTML', message_thread_id=message.message_thread_id)
                            else:
                                select = cur2.execute('select * from data where chat == ? and topic == ?',
                                                      (message.chat.id, message.message_thread_id)).fetchall()
                                for row in select:
                                    links = json.loads(row[4])
                                    for urs in new_urls:
                                        if urs in links:
                                            try:
                                                await bot.delete_message(row[1], row[0])
                                                cur2.execute('delete from data where chat == ? and id == ?', (row[0], row[0]))
                                                base2.commit()
                                            except:
                                                pass
                                cur2.execute('insert into data values (?, ?, ?, ?, ?)', (message.message_id, message.chat.id, message.message_thread_id, message.html_text, json.dumps(new_urls)))
                                base2.commit()


                        else:
                            await message.delete()



                            await bot.send_message(message.chat.id, f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, сообщение с такой ссылкой уже было опубликовано.',
                                                   parse_mode='HTML', message_thread_id=message.message_thread_id)
                    else:
                        await message.delete()
                        await bot.send_message(message.chat.id,
                                               f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, сообщение содержит запрещённую ссылку в данном топике',
                                               parse_mode='HTML', message_thread_id=message.message_thread_id)
                else:
                    await message.delete()
                    await bot.send_message(message.chat.id,
                                           f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, сообщение в этом топике должно содержать ссылку {prelink}',
                                           parse_mode='HTML', message_thread_id=message.message_thread_id)
            else:
                await message.delete()
                await bot.send_message(message.chat.id,
                                       f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>, сообщение обязательно должно содержать ссылку.',
                                       parse_mode='HTML', message_thread_id=message.message_thread_id)
