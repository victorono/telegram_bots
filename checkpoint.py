#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from datetime import datetime, timedelta
from time import mktime
# from pytz import timezone
# import pytz
from math import floor

import sqlite3

"""
CREATE TABLE `chat_settings` (
    `id`    INTEGER,
    `timezone`  TEXT,
    `language`  TEXT,
    `chat_id`   INT UNIQUE,
    PRIMARY KEY(`id`)
);
"""

EPOCH = 1389150000000
CYCLE_LENGTH = 630000000
CHECKPOINT_LENGTH = 18000


def save_settings(chat_id):

    conn = None
    table_name = 'chat_settings'
    id_column = 'chat_id'
    timezone = 'timezone'
    language = 'language'

    try:
        conn = sqlite3.connect('checkpoint_settings.db')
        c = conn.cursor()

        query = "SELECT * FROM {tn} WHERE {idf}={my_id};".format(tn=table_name, idf=id_column, my_id=chat_id)
        print(query)
        c.execute(query)
        chack_settings = c.fetchone()

        if chack_settings:
            print('{}'.format(chack_settings))
        else:

            query = "INSERT INTO {table_name} (chat_id, {timezone}, {language}) VALUES ({chat_id}, 'America/Santiago', 'es');".\
                format(chat_id=chat_id, timezone=timezone, language=language, table_name=table_name)
            try:
                print(query)
                c.execute(query)
                conn.commit()
            except sqlite3.IntegrityError:
                print('chat_id already exists in PRIMARY KEY column {}'.format(id_column))

    except sqlite3.Error as e:
        print('No se pudo conectar', e)

    finally:
        if conn:
            conn.close()


def current_cycle():
    present = datetime.now()
    tt = datetime.timetuple(present)
    now = mktime(tt) * 1000
    cycle = floor((now - EPOCH) / CYCLE_LENGTH)
    start = datetime.fromtimestamp(CHECKPOINT_LENGTH + ((EPOCH + (cycle * CYCLE_LENGTH)) / 1000))

    checkpoints = []
    for i in range(0, 35):
        next = (start > present) and (present + timedelta(seconds=CHECKPOINT_LENGTH)) > start
        cp = {
            'date': start.strftime('%a %d %b'),
            'time': start.strftime('%I:%M%p'),
            'next': next,
            'past': (start < present)
        }
        checkpoints.append(cp)
        start = start + timedelta(seconds=CHECKPOINT_LENGTH)
    return checkpoints


def next_checkpoint(cps):
    future = [cp for cp in cps if cp['past'] is False]
    return future[0]


def cycle_end(cps):
    return cps[-1]


def settings(bot, update, args):

    str_result = 'args: {} {}'.format(args[0], args[1])
    chat_id = update.message.chat.id

    save_settings(chat_id)

    update.message.reply_text(str_result)


def checkpoints(bot, update):

    chat_id = update.message.chat.id

    cps = current_cycle()
    n = next_checkpoint(cps)
    c = cycle_end(cps)
    str_result = "Next checkpoint is {} <b>{}</b>.\nThis cycle ends {} <b>{}</b>.".format(n['date'], n['time'], c['date'], c['time'])

    bot.sendMessage(chat_id=chat_id, text=str_result, parse_mode='HTML')


def all_cps(bot, update):

    t0 = datetime.strptime('2014-07-09 11', '%Y-%m-%d %H')
    hours_per_cycle = 175

    t = datetime.utcnow()

    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles = seconds // (3600 * hours_per_cycle)
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    checkpoints = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))

    for num, checkpoint in enumerate(checkpoints, start=1):
        print('%2d %s' % (num, checkpoint))


# TOKEN
updater = Updater('291331956:AAGTv3cpqPwRy6OYNRfNMUxns982JBQIzBA')

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('settings', settings, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('checkpoints', checkpoints))

updater.start_polling()
updater.idle()
