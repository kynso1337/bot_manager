import sqlite3

base = sqlite3.connect('databases/chats.db')
cur = base.cursor()
base.execute('create table if not exists {}(id integer, info text, settings text)'.format('data'))

base2 = sqlite3.connect('databases/messages.db')
cur2 = base2.cursor()
base2.execute('create table if not exists {}(id integer, chat integer, topic integer, message text, links text)'.format('data'))

base3 = sqlite3.connect('databases/topics.db')
cur3 = base3.cursor()
base3.execute('create table if not exists {}(chat integer, topic integer, name text, settings text)'.format('data'))
