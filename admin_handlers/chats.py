import json

from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatShared

from datetime import datetime
import pytz

from preload.functions import *


router = Router()
bot = Bot(TOKEN)


import logging
logging.basicConfig(level=logging.INFO, filename="logs/handlers.log",filemode="w")



@router.message(F.text == 'Чаты')
async def chatsFunc(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admin_ids:
        text, kbs = await generateChats()
        await message.answer(text, parse_mode='HTML', reply_markup=kbs)


@router.message(F.chat_shared)
async def mes_func(chat: ChatShared, state: FSMContext):
    if chat.from_user.id in admin_ids:
        await state.clear()
        if str(chat.chat_shared.chat_id).find('-100') == -1:
            chat_id = str(chat.chat_shared.chat_id).replace('-', '-100')
            chat_id = int(chat_id)
        else:
            chat_id = chat.chat_shared.chat_id

        chan = await bot.get_chat(chat_id)
        if len(cur.execute('select * from data where id == ?', (chat_id,)).fetchall()) == 0:
            date = datetime.now(pytz.timezone('Europe/Moscow'))
            date = str(date).split('.')[0]
            info = {
                'id': chat_id,
                'title': chan.title,
                'link': chan.invite_link,
                'date': date
            }
            cur.execute('insert into data values (?, ?, ?)', (chat_id, json.dumps(info), '[]'))
            base.commit()
            await bot.send_message(chat.from_user.id, f'Ты успешно подключил канал "{info["title"]}" к боту!')
            text, kbs = await generateChats()
            await bot.send_message(chat.from_user.id, text, parse_mode='HTML', reply_markup=kbs)
        else:
            await bot.send_message(chat.from_user.id, 'Такой канал уже подключён к боту!')


@router.callback_query(F.data.startswith('select_chat_'))
async def selectChatFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = int(callback.data.split('_')[-1])
    text, kbs = await generateOneChat(chat_id)
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kbs, disable_web_page_preview=True)


@router.callback_query(F.data == 'back_to_allchannels')
async def backToAllChannelsFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text, kbs = await generateChats()
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kbs)


@router.callback_query(F.data.startswith('delete_chat_'))
async def deleteChatFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = int(callback.data.split('_')[-1])
    select = cur.execute('select * from data where id == ?', (chat_id, )).fetchone()
    info = json.loads(select[1])
    kbs = [[InlineKeyboardButton(text = '✔️ Да, удалить', callback_data=f'yesdel_chat_{chat_id}')],
           [InlineKeyboardButton(text = '✖️ Нет, отмена', callback_data=f'select_chat_{chat_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    await callback.message.edit_text(f'Ты уверен, что хочешь удалить чат <b>"{info["title"]}"</b>?\n\n<i>После его удаления очистятся все шаблоны и база ссылок.</i>',
                                     parse_mode='HTML', reply_markup=kbs)

@router.callback_query(F.data.startswith('yesdel_chat_'))
async def yesDeleteChatFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = int(callback.data.split('_')[-1])
    cur.execute('delete from data where id == ?', (chat_id, ))
    base.commit()
    cur.execute('vacuum')
    cur2.execute('delete from data where chat == ?', (chat_id, ))
    base2.commit()
    cur2.execute('vacuum')
    await callback.answer('Канал успешно удалён!')
    text, kbs = await generateChats()
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kbs)

#chat integer, topic integer, name text, settings text
@router.callback_query(F.data.startswith('add_topic_'))
async def addTopicFunc(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split('_')[-1])
    kbs = [[InlineKeyboardButton(text = '← Назад', callback_data=f'select_chat_{chat_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    await callback.message.edit_text('Пришли мне айди топика', reply_markup=kbs)
    await state.set_state(aForm.topic_id)
    await state.update_data(chat_id = chat_id)

@router.message(F.text, aForm.topic_id)
async def topicIdFunc(message: Message, state: FSMContext):
    try:
        topic_id = int(message.text)
        await state.update_data(topic_id = topic_id)
        data = await state.get_data()
        chat_id = data['chat_id']
        kbs = [[InlineKeyboardButton(text='← Назад', callback_data=f'select_chat_{chat_id}')]]
        kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
        await message.answer('Теперь пришли мне отображаемое название для топика', reply_markup=kbs)
        await state.set_state(aForm.topic_name)
    except:
        await message.answer('Айди должен быть числом.')
#chat integer, topic integer, name text, settings text
@router.message(F.text, aForm.topic_name)
async def topicNameFunc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    topic_id = data['topic_id']
    settings = {
        'points': [],
        'link': ''
    }
    cur3.execute('insert into data values (?, ?, ?, ?)', (chat_id, topic_id, message.text, json.dumps(settings)))
    base3.commit()
    await message.answer(f'Топик "{message.text}" успешно добавлен!')
    text, kbs = await generateTopic(chat_id, topic_id)
    await bot.send_message(message.from_user.id, text, parse_mode='HTML', reply_markup=kbs, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('select_topic'))
async def selectTopicFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = callback.data.split('_')[-2]
    topic_id = callback.data.split('_')[-1]
    text, kbs = await generateTopic(chat_id, topic_id)
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kbs, disable_web_page_preview=True)

@router.callback_query(F.data.startswith('pattern_settings_'))
async def patternSettingsFunc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = int(callback.data.split('_')[-2])
    topic_id = int(callback.data.split('_')[-1])
    text, kbs = await generatePatternSettings(chat_id, topic_id)
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kbs)


@router.callback_query(F.data.startswith('add_point_'))
async def addPointFunc(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.data.split('_')[-2]
    topic_id = callback.data.split('_')[-1]
    kbs = [[InlineKeyboardButton(text = '← Назад', callback_data=f'select_topic_{chat_id}_{topic_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    await callback.message.edit_text('Пришли мне текст нового пункта', reply_markup=kbs)
    await state.set_state(aForm.add_point)
    await state.update_data(chat_id = chat_id, topic_id = topic_id)

@router.message(F.text, aForm.add_point)
async def newPointFunc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    topic_id = data['topic_id']
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    settings['points'].append(message.text)
    cur3.execute('update data set settings == ? where chat == ? and topic == ?', (json.dumps(settings), chat_id, topic_id))
    base3.commit()
    text, kbs = await generatePatternSettings(chat_id, topic_id)
    await message.answer(f'Ты успешно добавил пункт "{message.text}"')
    await bot.send_message(message.from_user.id, text, parse_mode='HTML', reply_markup=kbs)
    await state.clear()


@router.callback_query(F.data.startswith('delete_point_'))
async def delPointFunc(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.data.split('_')[-2]
    topic_id = callback.data.split('_')[-1]
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    text = '\n'.join(f'{i+1}. {set}' for i, set in enumerate(settings['points']))

    kbs = [[InlineKeyboardButton(text = '← Назад', callback_data=f'pattern_settings_{chat_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    await callback.message.edit_text(f'{text}\n\nПришли мне номер пункта, который хочешь удалить.', reply_markup=kbs)
    await state.set_state(aForm.del_point)
    await state.update_data(chat_id = chat_id, topic_id = topic_id)

@router.message(F.text, aForm.del_point)
async def deletePointFunc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    topic_id = data['topic_id']
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    try:
        point = settings['points'][int(message.text)-1]
        del settings['points'][int(message.text)-1]
        cur3.execute('update data set settings == ? where chat == ? and topic == ?', (json.dumps(settings), chat_id, topic_id))
        base3.commit()
        text, kbs = await generatePatternSettings(chat_id, topic_id)
        await message.answer(f'Ты успешно удалил пункт "{point}"')
        await bot.send_message(message.from_user.id, text, parse_mode='HTML', reply_markup=kbs)
        await state.clear()
    except:
        await message.answer('Необходимо прислать только число')


@router.callback_query(F.data.startswith('edit_link_'))
async def editLinkFunc(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split('_')[-2])
    topic_id = int(callback.data.split('_')[-1])
    kbs = [[InlineKeyboardButton(text = '← Назад', callback_data=f'pattern_settings_{chat_id}')]]
    kbs = InlineKeyboardMarkup(inline_keyboard=kbs)
    await callback.message.edit_text('Пришли мне ссылку', reply_markup=kbs)
    await state.set_state(aForm.new_link)
    await state.update_data(chat_id = chat_id, topic_id = topic_id)

@router.message(F.text, aForm.new_link)
async def newLinkFunc(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['chat_id']
    topic_id = data['topic_id']
    select = cur3.execute('select * from data where chat == ? and topic == ?', (chat_id, topic_id)).fetchone()
    settings = json.loads(select[3])
    settings['link'] = message.text
    cur3.execute('update data set settings == ? where chat == ? and topic == ?', (json.dumps(settings), chat_id, topic_id))
    base3.commit()
    text, kbs = await generateTopic(chat_id, topic_id)
    await message.answer(f'Ты успешно обновил ссылку на "{message.text}"')
    await bot.send_message(message.from_user.id, text, parse_mode='HTML', reply_markup=kbs, disable_web_page_preview=True)
    await state.clear()