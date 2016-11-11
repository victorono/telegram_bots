#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from datetime import datetime, timedelta
from time import mktime
from pytz import timezone

import sqlite3
import pytz

"""
CREATE TABLE `chat_settings` (
    `id`    INTEGER,
    `timezone`  TEXT,
    `language`  TEXT,
    `chat_id`   INT UNIQUE,
    PRIMARY KEY(`id`)
);
"""


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


def start(bot, update):
    update.message.reply_text('Hello World!')


def help(bot, update):
    str_result = '=)'
    update.message.reply_text(str_result)


def settings(bot, update, args):

    str_result = 'args: {} {}'.format(args[0], args[1])
    chat_id = update.message.chat.id

    save_settings(chat_id)

    update.message.reply_text(str_result)


def checkpoints(bot, update):

    t0 = datetime.strptime('2015-06-24 20', '%Y-%m-%d %H').replace(tzinfo=timezone('America/Santiago'))
    hours_per_cycle = 175
    hours_per_cp = 5
    t = datetime.now().replace(tzinfo=timezone('America/Santiago'))

    seconds_from_t0 = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles_from_t0 = seconds_from_t0 // (3600 * hours_per_cycle)
    cycle_start = t0 + timedelta(hours=cycles_from_t0 * hours_per_cycle)
    cycle_end = cycle_start + timedelta(hours=hours_per_cycle)

    seconds_from_cycle_start = mktime(t.timetuple()) - mktime(cycle_start.timetuple())
    next_cp_num = (seconds_from_cycle_start // (3600 * hours_per_cp)) + 1   # +1 -- rounding up
    next_cp = cycle_start + timedelta(hours=(next_cp_num) * hours_per_cp)

    rem_cycle = cycle_end - t
    rem_hours = rem_cycle.seconds // 3600
    rem_minutes = (timedelta(seconds=rem_cycle.seconds) - timedelta(hours=rem_hours)).seconds // 60

    text_return = "CP#{!s} en: {!s}, a las: {:%H:%M} \r\nCiclo termina en {!s} dias {!s} horas {!s} min el {:%Y-%m-%d %H:%M}"

    str_result = text_return.format(int(next_cp_num), ':'.join(str(next_cp - t).split(':')[:2]), next_cp, rem_cycle.days, rem_hours, rem_minutes, cycle_end)

    update.message.reply_text(str_result)


# TOKEN
updater = Updater('291331956:AAGTv3cpqPwRy6OYNRfNMUxns982JBQIzBA')

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('settings', settings, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('checkpoints', checkpoints))

updater.start_polling()
updater.idle()
