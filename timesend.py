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
from bot_add import convert_time

os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()





sched2 = BlockingScheduler()




def addnewsheduler(time, user_id):
    curs.execute("SELECT parse_mode FROM users WHERE telegram_id='{}'".format(user_id))
    previous_time = curs.fetchone()[0]

    print('previous_time',previous_time)
    print('new_time',time)

    if previous_time in ['immediate', 'everyhour']:
        previous_time = ''
    else:
        previous_time = str(previous_time) + ', '

    print('previous_time',previous_time)

    # if str(hours) + ':' + str(minutes) not in customtime:
    #new_time = str(hours) + ':' + str(minutes)

    new_time = previous_time + time[0] #', '.join(list(set(new_time.split(', ')))) #removes duplicates from time list

    print('customtime', new_time)

    curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id='{}'".format(new_time, user_id))
    conn.commit()
    #hours = ''
    #minutes = ''


@sched2.scheduled_job('interval', minutes=1)
def specific_time_send():
    print('every minute!')
    now_hour = str(datetime.now().time()).split(':')[0]
    now_minute = str(datetime.now().time()).split(':')[1]
    print(now_hour, now_minute)
    now_time = now_hour+':'+now_minute

    try:
        curs.execute("SELECT * FROM users")
        users = curs.fetchall()
    except:
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Сталася проблема комунікації з базою даних. Пробую відновити зв\'язок!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Сталася проблема комунікації з базою даних. Пробую відновити зв\'язок!'))
        curs.execute("Rollback")
        conn.commit()
        curs.execute("SELECT * FROM users")
        users = curs.fetchall()
        if users:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Проблему вирішено! Стабільну роботу відновлено!'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Проблему вирішено! Стабільну роботу відновлено!'))


    send_result = []
    for i in users:
        try:
            print('Another user: ' + i[2])
            time_send = i[7]
            timezone = i[16]
            if ':' in time_send:
                if ',' in time_send:
                    time=time_send.split(', ')
                    time = convert_time(time, timezone)
                else:
                    time=[time_send]
                    time = convert_time(time, timezone)

                local_time = convert_time([now_time], timezone)

                print(local_time, time)

                if local_time[0] in time:
                    length = send([i])
                    updateNewsSent(length, i)
                    send_result.append(str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]))
                    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Надіслано '+ str(length) + ' новин користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]) + '.\nЛокальний час: '+ str(local_time[0]))
                    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Надіслано '+ str(length) + ' новин користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]) + '.\nЛокальний час: '+ str(local_time[0]))
            elif time_send == 'everyhour':
                print('everyhour', now_time, timezone)
                time = convert_time([now_time], timezone)[0]
                print(str(time))
                local_hour = int(time.split(':')[0])
                local_minute = int(time.split(':')[1])
                if local_minute == 0 and local_hour >= 7 and local_hour <=23:
                    length = send([i])
                    updateNewsSent(length, i)
                    send_result.append(str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]))
                    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Надіслано '+ str(length) + ' новин користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]) + '.\nЛокальний час: '+ str(time))
                    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Надіслано '+ str(length) + ' новин користувачу ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]) + '.\nЛокальний час: '+ str(time))
        except Exception as e:
            print('Error sending news to user!')
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Error sending news to user! ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Error sending news to user! ' +str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '.\nЧас отримання новин: '+ str(i[7])) + '.\nGMT: '+ str(i[16]))
            continue

    if len(send_result) > 1:
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Підсумок:\nФункція надсилання спрацювала для ' +str(len(send_result)) + ' користувачів'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Підсумок:\nФункція надсилання спрацювала для ' +str(len(send_result)) + ' користувачів'))


    if now_hour == '21' and now_minute == '34':
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Час підбити підсумки дня!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Час підбити підсумки дня!'))

        sum = 0
        users_received_today = 0
        not_received = 0
        for i in users:
            if int(i[24]) == 0:
                curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(i[1]))
                websites = ''
                for b in curs.fetchall():
                    curs.execute("SELECT name FROM websites WHERE id='{}'".format(b[0]))
                    websites = websites + curs.fetchone()[0] + ', '

                timezone = i[16]
                parse_mode = i[7]

                if ':' in parse_mode:
                    print(parse_mode)
                    if ',' in parse_mode:
                        times = convert_time(parse_mode.split(', '), timezone)
                        times = ', '.join(times)
                    else:
                        times = convert_time([parse_mode], timezone)[0]
                else:
                    times = parse_mode

                requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Користувачу '+ i[2] + ' ' + i[9] + ' ' + i[10] + ' (' + str(i[1]) +')' +' сьогодні не надіслано новини. Теми юзера: ' +str(i[6]) + '. Сайти: '+ websites + '. Час: '+ times))
                requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Користувачу '+ i[2] + ' ' + i[9] + ' ' + i[10] + ' (' + str(i[1]) +')' +' сьогодні не надіслано новини. Теми юзера: ' +str(i[6]) + '. Сайти: '+ websites + '. Час: '+ times))
                not_received += 1
            else:
                users_received_today += 1
            sum += int(i[24])

        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Сьогодні було надіслано ' + str(sum) + ' статей\nНовини отримали '+ str(users_received_today) + ' користувачів\nНовини не отримали '+ str(not_received)+ ' користувачів'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Сьогодні було надіслано ' + str(sum) + ' статей\nНовини отримали '+ str(users_received_today) + ' користувачів\nНовини не отримали '+ str(not_received)+ ' користувачів'))

        curs.execute("UPDATE users SET news_sent_today = 0")
        conn.commit()
    # if now_hour == '07' and now_minute == '01':
    #     curs.execute("SELECT value FROM static WHERE name ='9am'")
    #     if curs.fetchone()[0] != 'ok':
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 ранку не відбулася! Стартую ще раз!'))
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 9 ранку не відбулася! Стартую ще раз!'))
    #         nine_am()
    #
    # if now_hour == '10' and now_minute == '00':
    #     twelve_am()
    # if now_hour == '10' and now_minute == '01':
    #     curs.execute("SELECT value FROM static WHERE name ='12am'")
    #     if curs.fetchone()[0] != 'ok':
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 12 дня не відбулася! Стартую ще раз!'))
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 12 дня не відбулася! Стартую ще раз!'))
    #         twelve_am()
    #
    # if now_hour == '19' and now_minute == '00':
    #     nine_pm()
    # if now_hour == '19' and now_minute == '01':
    #     curs.execute("SELECT value FROM static WHERE name ='9pm'")
    #     if curs.fetchone()[0] != 'ok':
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 12 дня не відбулася! Стартую ще раз!'))
    #         requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 12 дня не відбулася! Стартую ще раз!'))
    #         nine_pm()
    #
    #
    # if now_hour in ['5', '6', '8', '9', '11', '12', '13', '14', '15', '16', '17', '18', '20', '21'] and now_minute == '00':
    #     print('РОЗСИЛКА ЮЗЕРАМ ЩОГОДИНИ')
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
    #     curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
    #     users = curs.fetchall()
    #     send(users)
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
    #
    # if now_hour == '22' and now_minute == '00':
    #     # онулити значення ok в базі даних
    #     curs.execute("UPDATE static SET value ='' WHERE name ='9pm'")
    #     curs.execute("UPDATE static SET value ='' WHERE name ='9am'")
    #     curs.execute("UPDATE static SET value ='' WHERE name ='12am'")
    #     conn.commit()
    #
    # if now_minute == '00':
    #     print('РОЗСИЛКА ЮЗЕРАМ ЩОГОДИНИ')
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
    #     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
    #     curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
    #     users = curs.fetchall()
    #     for i in users:
    #         timezone = i[16]
    #         local_time = convert_time(now_hour)




# def nine_am():
#     print('РОЗСИЛКА ЮЗЕРАМ О 9 РАНКУ')
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
#
#
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині ранку стартувала!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 9 годині ранку стартувала!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='9am'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('parsing finished!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('parsing finished!'))
#
#     curs.execute("UPDATE static SET value ='ok' WHERE name ='9am'")
#     conn.commit()
#
# def twelve_am():
#     print('РОЗСИЛКА ЮЗЕРАМ О 12 ДНЯ')
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
#
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 12 годині стартувала!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 12 годині стартувала!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='12am'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
#
#     curs.execute("UPDATE static SET value ='ok' WHERE name ='12am'")
#     conn.commit()
#
# def nine_pm():
#     print('РОЗСИЛКА ЮЗЕРАМ О 9 ВЕЧОРА')
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам щогодини стартувала!!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
#
#
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині вечора стартувала!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Розсилка юзерам о 9 годині вечора стартувала!'))
#     curs.execute("SELECT * FROM users WHERE parse_mode ='9pm'")
#     users = curs.fetchall()
#     send(users)
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))
#     requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Процес надсилання завершено!'))
#
#     curs.execute("UPDATE static SET value ='ok' WHERE name ='9pm'")
#     conn.commit()

def updateNewsSent(length, i):
    print('started', i)
    try:
        news_sent = int(i[23]) + int(length)
        news_sent_today = int(i[24]) + int(length)
        print(news_sent, news_sent_today)
        curs.execute("UPDATE users SET news_sent='{}', news_sent_today ='{}' WHERE telegram_id='{}'".format(news_sent, news_sent_today, i[1]))
        conn.commit()
    except TypeError:
        pass
    print('finished!')

if __name__ == '__main__':
    specific_time_send()
    sched2.start()
