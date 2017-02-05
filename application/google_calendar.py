from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

import numpy as np

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'config/client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

time_table = []

for h in range(9, 18):
    time1 = datetime.time(h, 15, 0)
    time2 = datetime.time(h, 45, 0)
    time_table.append(time1)
    time_table.append(time2)

def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_upcoming_events(calendar_id='primary', max_results=10):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming {} events'.format(max_results))
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=max_results, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []
    else:
        return events


def extract_datetime(datetime_text):
    ymd, time = datetime_text.split('T')
    year, month, date = ymd.split('-')
    hms, _ = time.split('+')
    hour, minute, second = hms.split(':')
    return year, month, date, hour, minute, second


def events2text(calendar_id, person, max_results=100):
    events = get_upcoming_events(calendar_id, max_results)
    text = '\n'
    text += person + 'さん\n'

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        summary = event['summary']
        sy, smo, sd, sh, smi, ss = extract_datetime(start)
        ey, emo, ed, eh, emi, es = extract_datetime(end)
        text += '{}/{} {}:{}〜{}:{} {}\n'.format(smo, sd, sh, smi, eh, emi, summary)

    return text

def events2array(calendar_id='primary', max_results=10):
    events_dic = {}
    all_events = []
    for i in range(len(calendar_id)):
        events = get_upcoming_events(calendar_id[i], max_results)
        all_events.append(events)

    for events in all_events:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            sy, smo, sd, sh, smi, ss = extract_datetime(start)
            ey, emo, ed, eh, emi, es = extract_datetime(end)

            stime = datetime.time(int(sh), int(smi), 0)
            etime = datetime.time(int(eh), int(emi), 0)

            day = smo + '-' + sd

            if day not in events_dic:
                events_dic[day] = time2array(stime, etime)
            else:
                a = events_dic[day]
                b = time2array(stime, etime)
                events_dic[day] = np.logical_and(a, b)

    return events_dic

def time2array(start, end):
    freetime_list = []
    for tt in time_table:
        if start < tt and tt < end:
            freetime_list.append(0)
        else:
            freetime_list.append(1)

    freetime_array = np.array(freetime_list, dtype=bool)

    return freetime_array

def array2text(array):
    text = ''
    for i in range(len(array)):
        if array[i] == True:
            if time_table[i].minute == 15:
                text += '{}:{}〜{}:{}\n'.format(time_table[i].hour, '00',\
                                                                   time_table[i].hour, time_table[i].minute + 15)
            elif time_table[i].minute == 45:
                text += '{}:{}〜{}:{}\n'.format(time_table[i].hour, time_table[i].minute - 15, \
                                                                   time_table[i].hour + 1, '00')

    return text

def freetime2text(calendar_id):
    text = '\n'

    freetime_dic = events2array(calendar_id)

    for k, v in sorted(freetime_dic.items()):
        text += k + '\n'
        text += array2text(v) + '\n'

    return text

def score(calendar_id='primary', max_results=10):
    events = get_upcoming_events(calendar_id, max_results)
    events_dic = {}
    scores_dic = {}
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        sy, smo, sd, sh, smi, ss = extract_datetime(start)
        ey, emo, ed, eh, emi, es = extract_datetime(end)

        stime = datetime.time(int(sh), int(smi), 0)
        etime = datetime.time(int(eh), int(emi), 0)

        day = datetime.datetime(int(sy), int(smo), int(sd))

        if day not in events_dic:
            events_dic[day] = time2array(stime, etime)
        else:
            a = events_dic[day]
            b = time2array(stime, etime)
            events_dic[day] = np.logical_and(a, b)

    for k, v in sorted(events_dic.items()):
        scores_dic[k] = len(v) - np.count_nonzero(v)

    return scores_dic

def recomend2text(calendar_id):
    text = '\n'

    score_dic = {}
    day_list = []
    for i in range(len(calendar_id)):
        cid = calendar_id[i]
        scores = score(calendar_id=cid)
        for k, v in scores.items():
            if k not in score_dic:
                score_dic[k] = [0, 0, 0]
                score_dic[k][i] = v
                day_list.append(k)
            else:
                score_dic[k][i] = v

    sort_day_list = sorted(day_list)

    ans_dic1 = {}
    ans_dic2 = {}

    for j in range(len(sort_day_list)):
        sd = sort_day_list[j]
        sd_y = sd - datetime.timedelta(days=1)
        sd_t = sd + datetime.timedelta(days=1)

        if sd_y in score_dic and sd_t in score_dic:
            score_sum = [x + y + z for (x, y, z) in zip(score_dic[sd_y], score_dic[sd], score_dic[sd_t])]
            # print(sd, 'y:' ,score_dic[sd_y], 'td:', score_dic[sd], 'tm:', score_dic[sd_t], 'sum:', score_sum)

        elif sd_y in score_dic and sd_t not in score_dic:
            score_sum = [x + y for (x, y) in zip(score_dic[sd_y], score_dic[sd])]
            # print(sd, 'y:' ,score_dic[sd_y], 'td:', score_dic[sd], 'tm:', [0, 0, 0], 'sum:', score_sum)

        elif sd_y not in score_dic and sd_t in score_dic:
            score_sum = [x + y for (x, y) in zip(score_dic[sd], score_dic[sd_t])]
            # print(sd, 'y:' ,[0, 0, 0], 'td:', score_dic[sd], 'tm:', score_dic[sd_t], 'sum:', score_sum)

        else:
            score_sum = score_dic[sd]
            # print(sd, 'y:' ,score_dic[sd], 'td:', [0, 0, 0], 'tm:', score_dic[sd], [0, 0, 0], 'sum:', score_sum)

        ans_dic1[sd] = max(score_sum)
        ans_dic2[sd] = score_sum

    c = 0
    for k, v in sorted(ans_dic1.items(), key=lambda x: x[1]):
        c += 1
        if c < 4:
            strk = str(k)
            text += strk[5:10] + 'を' + str(c) + '番におすすめします！\n'
            text += '当日および前後二日間の予定時間の合計は・・・'
            text += 'Aさん:' + str(ans_dic2[k][0] / 2)\
                    + '時間 / Bさん:' + str(ans_dic2[k][1] / 2)\
                    + '時間 / Cさん:' + str(ans_dic2[k][2] / 2) + '時間です！\n'
            text += '---------------------------------------------------------------------------------------------------------------------------------------\n'

    return text

def search2text(calendar_id, keyword, person, max_results=10):
    events = get_upcoming_events(calendar_id, max_results)
    text = '\n'

    text += person + 'さん\n'

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        summary = event['summary']
        sy, smo, sd, sh, smi, ss = extract_datetime(start)
        ey, emo, ed, eh, emi, es = extract_datetime(end)

        if keyword in summary:
            text += '{}/{} {}:{}〜{}:{} {}\n'.format(smo, sd, sh, smi, eh, emi, summary)

    return text

if __name__ == '__main__':
    calendar_id = ['hoge@group.calendar.google.com',\
                   'hogehoge@group.calendar.google.com',\
                   'hogehogehoge@group.calendar.google.com']

    """
    text = ''
    freetime_dic = events2array(calendar_id)

    for k, v in sorted(freetime_dic.items()):
        text += k + '\n'
        text += array2txt(v) + '\n'

    print(text)
    """

    """
    score_dic = {}
    day_list = []
    for i in range(len(calendar_id)):
        cid = calendar_id[i]
        scores = score(calendar_id=cid)
        for k, v in scores.items():
            if k not in score_dic:
                score_dic[k] = [0, 0, 0]
                score_dic[k][i] = v
                day_list.append(k)
            else:
                score_dic[k][i] = v

    sort_day_list = sorted(day_list)

    ans_dic1 = {}
    ans_dic2 = {}

    for j in range(len(sort_day_list)):
        sd = sort_day_list[j]
        sd_y = sd - datetime.timedelta(days=1)
        sd_t = sd + datetime.timedelta(days=1)

        if sd_y in score_dic and sd_t in score_dic:
            score_sum = [x + y + z for (x, y, z) in zip(score_dic[sd_y], score_dic[sd], score_dic[sd_t])]
            #print(sd, 'y:' ,score_dic[sd_y], 'td:', score_dic[sd], 'tm:', score_dic[sd_t], 'sum:', score_sum)
            ans_dic1[sd] = max(score_sum)
            ans_dic2[sd] = score_sum

        elif sd_y in score_dic and sd_t not in score_dic:
            score_sum = [x + y for (x, y) in zip(score_dic[sd_y], score_dic[sd])]
            #print(sd, 'y:' ,score_dic[sd_y], 'td:', score_dic[sd], 'tm:', [0, 0, 0], 'sum:', score_sum)
            ans_dic1[sd] = max(score_sum)
            ans_dic2[sd] = score_sum

        elif sd_y not in score_dic and sd_t in score_dic:
            score_sum = [x + y for (x, y) in zip(score_dic[sd], score_dic[sd_t])]
            #print(sd, 'y:' ,[0, 0, 0], 'td:', score_dic[sd], 'tm:', score_dic[sd_t], 'sum:', score_sum)
            ans_dic1[sd] = max(score_sum)
            ans_dic2[sd] = score_sum

        else:
            score_sum = score_dic[sd]
            #print(sd, 'y:' ,score_dic[sd], 'td:', [0, 0, 0], 'tm:', score_dic[sd], [0, 0, 0], 'sum:', score_sum)
            ans_dic1[sd] = max(score_sum)
            ans_dic2[sd] = score_sum

    c = 0
    for k, v in sorted(ans_dic1.items(), key=lambda x: x[1]):
        c += 1
        if c < 4:
            strk = str(k)
            print(strk[5:10], 'が', str(c), '番におすすめです！')
            print('Aさん:' ,ans_dic2[k][0] / 2,\
                  '時間 / Bさん:' ,ans_dic2[k][1] / 2,\
                  '時間 / Cさん:' ,ans_dic2[k][2] / 2, '時間')
    """