# -*- coding: utf-8 -*-
import sys
from slackbot.bot import respond_to
sys.path.append('..')
from google_calendar import events2text, freetime2text, recomend2text

calendar_id = ['', \
                   '', \
                   '']

persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

@respond_to('今後の予定')
def respond_schedule(message):
    for i in range(len(calendar_id)):
        reply_message = events2text(calendar_id=calendar_id[i])
        message.reply(reply_message)


@respond_to('空き時間')
def respond_freetime(message):
    reply_message = freetime2text(calendar_id=calendar_id)
    message.reply(reply_message)

@respond_to('おすすめ')
def respond_recomend(message):
    reply_message = recomend2text(calendar_id=calendar_id)
    message.reply(reply_message)