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
from parse import parse, remove_bad_characters, send, timed_job


os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()





sched2 = BlockingScheduler()




def addnewsheduler(hours, minutes, user_id):
    curs.execute("SELECT parse_mode FROM users WHERE telegram_id='{}'".format(user_id))
    previous_time = curs.fetchone()[0]

    print(previous_time)

    # if str(hours) + ':' + str(minutes) not in customtime:
    new_time = str(previous_time) + ', ' + str(hours) + ':' + str(minutes)

    new_time = ', '.join(list(set(new_time.split(', ')))) #removes duplicates from time list

    print('customtime', new_time)

    curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id='{}'".format(new_time, user_id))
    conn.commit()
    hours = ''
    minutes = ''


@sched2.scheduled_job('interval', minutes=1)
def specific_time_send():
    print('every minute!')
    now_hour = str(datetime.now().time()).split(':')[0]
    now_minute = str(datetime.now().time()).split(':')[1]
    print(now_hour, now_minute)
    now_time = now_hour+':'+now_minute
    curs.execute("SELECT * FROM users")
    users = curs.fetchall()
    for i in users:
        time_send = i[7]
        if ':' in time_send:
            if ',' in time_send:
                time=time_send.split(', ')
            else:
                time=[time_send]

            if now_time in time:
                send([i])
                requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Надіслано новини користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10])))
                requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=373407132&text={}'.format('Надіслано новини користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10])))

    if now_hour == '7' and now_minute == '00':
        print('РОЗСИЛКА ЮЗЕРАМ О 9 РАНКУ')
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))


        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині ранку стартувала!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 9 годині ранку стартувала!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='9am'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('parsing finished!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('parsing finished!'))

    if now_hour == '10' and now_minute == '00':
        print('РОЗСИЛКА ЮЗЕРАМ О 12 ДНЯ')
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))


        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 12 годині стартувала!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 12 годині стартувала!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='12am'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))

    if now_hour == '19' and now_minute == '00':
        print('РОЗСИЛКА ЮЗЕРАМ О 9 ВЕЧОРА')
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))


        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині вечора стартувала!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 9 годині вечора стартувала!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='9pm'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))

    if now_hour in ['5', '6', '8', '9', '11', '12', '13', '14', '15', '16', '17', '18', '20', '21'] and now_minute == '00':
        print('РОЗСИЛКА ЮЗЕРАМ ЩОГОДИНИ')
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
        curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
        users = curs.fetchall()
        send(users)
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))








if __name__ == '__main__':

    specific_time_send()
    sched2.start()
