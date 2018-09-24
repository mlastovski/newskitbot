# -*-coding: utf-8 -*-
import os
import requests
import psycopg2
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from parsers.two_four_tvua import parse_24tvua
from parsers.ain import parse_ainua
from parsers.wylsacom import wylsa
from parsers.appleinsider import appleinsider
from parsers.dou import dou
from parsers.pravda import pravda
from parsers.faktyICTV import faktyictv
from parsers.hromadske import hromadske
from parsers.korrespondent import korrespondent
from parsers.onehundredtwelve import onehundredtwelve
from parsers.isport import isport
from parsers.spiegelDeutsch import spiegelDeutsch
from parse import parse, remove_bad_characters, send


os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()





sched2 = BlockingScheduler()




def addnewsheduler(hours, minutes, user_id):
    curs.execute("SELECT value FROM static WHERE id=3")
    customtime = curs.fetchone()[0].split(', ')
    print(customtime)

    curs.execute("SELECT parse_mode FROM users WHERE telegram_id='{}'".format(user_id))
    previous_time = curs.fetchone()[0]

    if ':' in str(previous_time):
        print('ya')
        customtime.remove(str(previous_time))
        print('ya')

    print(customtime)

    if str(hours) + ':' + str(minutes) not in customtime:
        customtime.append(str(hours) + ':' + str(minutes))
        print('customtime', ', '.join(customtime))
        curs.execute("UPDATE static SET value = '{}' WHERE id=3".format(', '.join(customtime)))
        conn.commit()

    curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id='{}'".format(str(hours) + ':' + str(minutes), user_id))
    conn.commit()
    hours = ''
    minutes = ''
    for time in customtime:
        if hours=='':
            hours = hours + time.split(':')[0]
            minutes = minutes + time.split(':')[1]
        else:
            hours = hours + ',' + time.split(':')[0]
            minutes = minutes + ',' + time.split(':')[1]

    print(hours)
    print(minutes)

    #sched2.add_job(timed_job4, 'cron', id='my_cron_job1', hour='22,23,22', minute ='29,30,31')
    #sched2.add_job(specific_time_send, 'cron', id='my_cron_job1', hour=str(hours), minute =str(minutes))
    #sched2.start()

#
# @sched.scheduled_job('cron', hour='19,20,21', minute='40,10,02')
def timed_job4():
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('From here!'))

@sched2.scheduled_job('interval', minutes=1)
def specific_time_send():
    now_hour = str(datetime.now().time()).split(':')[0]
    now_minute = str(datetime.now().time()).split(':')[1]
    curs.execute("SELECT * FROM users WHERE parse_mode='{}'".format(now_hour+':'+now_minute))
    users = curs.fetchall()
    send(users)
    if users:
        requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('specific time'))
        requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=373407132&text={}'.format('specific time'))







if __name__ == '__main__':

    specific_time_send()
    sched2.start()
