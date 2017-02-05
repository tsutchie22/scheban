# -*- coding: utf-8 -*-
import sys
from slackbot.bot import respond_to, listen_to
sys.path.append('..')
from google_calendar import events2text, freetime2text, recomend2text, search2text
from weather import weather2text

calendar_id = ['hoge@group.calendar.google.com',\
                   'hogehoge@group.calendar.google.com',\
                   'hogehogehoge@group.calendar.google.com']

persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

@respond_to('こんにちは')
@respond_to('今日は')
def hello1(message):
    message.reply('こんにちは!')

@listen_to('私は(.*)です')
@listen_to('わたしは(.*)です')
def hello2(message, something):
    message.reply('こんにちは!{0}さん。'.format(something))

@respond_to('スケジュール')
def respond_schedule(message):
    for i in range(len(calendar_id)):
        reply_message = events2text(calendar_id=calendar_id[i], person=persons[i])
        message.reply(reply_message)

@respond_to('空き時間')
def respond_freetime(message):
    reply_message = freetime2text(calendar_id=calendar_id)
    message.reply(reply_message)

@respond_to('おすすめ')
def respond_recomend(message):
    reply_message = recomend2text(calendar_id=calendar_id)
    message.reply(reply_message)

@respond_to('(.*)の予定')
def respond_search(message, something):
    for i in range(len(calendar_id)):
        reply_message = search2text(calendar_id=calendar_id[i], keyword=something, person=persons[i])
        message.reply(reply_message)

@listen_to('天気')
def respond_weather(message):
    reply_message = weather2text()
    message.reply(reply_message)