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


os.environ['DATABASE_URL'] = 'postgres://vudojolxpbdbhu:57eaedbba34bb27f944556c177049db7a50068fbc0eca8ffe161f5e7b072d325@ec2-54-217-235-166.eu-west-1.compute.amazonaws.com:5432/dckdtc2c8arian'

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()


def parse(media):
    print(media)
    from bot import get_json_from_url

    if media == 1:
        parsed_content = wylsa()
        web_name = 'wylsa.com'
    elif media == 2:
        parsed_content = parse_24tvua()
        web_name = '24канал'
    elif media == 3:
        parsed_content = parse_ainua()
        web_name = 'ain.ua'
    elif media == 4:
        parsed_content = appleinsider()
        web_name = 'appleinsider.ru'
    elif media == 5:
        parsed_content = dou()
        web_name = 'dou.ua'
    #elif media == 6:
    #    parsed_content = pravda()
    #    web_name = 'українська правда'
    elif media == 7:
        parsed_content = faktyictv()
        web_name = 'факти ictv'
    elif media == 8:
        parsed_content = hromadske()
        web_name = 'hromadske'
    elif media == 9:
        parsed_content = korrespondent()
        web_name = 'korrespondent'
    elif media == 10:
        parsed_content = onehundredtwelve()
        web_name = '112.ua'
    elif media == 11:
        parsed_content = isport()
        web_name = 'isport.ua'
    else:
        return None

    print('Parsing ', web_name)

    id = media
    print(parsed_content)

    links = []
    for item in parsed_content:
        link = item['link']
        links.append(link)

    curs.execute("SELECT * FROM articles WHERE website_id ='{}' ORDER BY ID DESC LIMIT 1".format(id))
    last_article = curs.fetchone()

    print(links)
    print(last_article)

    if not last_article:
        logic=False
    elif last_article[2] in links:
        logic=True
    else:
        logic=False

    timeofday = round(datetime.now().timestamp() % 86400, 3)
    if timeofday > 0.875 and timeofday < 0.208:
        nightsleep = True
    else:
        nightsleep = False

    print('nightsleep', nightsleep)

    if logic: #last_article[2] in links:
        index = links.index(last_article[2])
        print('Sending content of ', web_name)

        for new_article_number in range(index-1, -1, -1):
            print(new_article_number)
            new_article = parsed_content[new_article_number]

            #defining article keywords by its header
            title = remove_bad_characters(new_article['title'].split())

            curs.execute("SELECT keywords FROM users")
            keywords_all = list(curs.fetchall())
            keywords_all_new = []
            for words in keywords_all:
                try:
                    el_list = words[0].split(', ')
                    keywords_all_new = keywords_all_new  + el_list
                except AttributeError:
                    print('error')

            keywords_all = []
            for i in keywords_all_new:
                if i not in keywords_all and i != '':
                    keywords_all.append(i)

            print('all keywords:', keywords_all)
            #endof getting all keywords list, we get keywords_all variable with all of them

            #comparing title words with already existing keywords
            article_keywords = []
            for word in title:
                if word in keywords_all:
                    article_keywords.append(word)

            print('title', title)
            print('keywords in article: ', article_keywords)

            article_keywords = ', '.join(article_keywords)
            print('got an article!')
            try:
                curs.execute("INSERT INTO articles (website_id, url, keywords, parse_time)  VALUES ('{}','{}','{}', '{}')".format(id, new_article['link'], article_keywords, datetime.now().timestamp()))
                conn.commit()
                duplicate = False
                print('article inserted!')
            except psycopg2.IntegrityError:
                print('duplicate')
                duplicate = True
                curs.execute("ROLLBACK")
                conn.commit()

            print('i handled an article!')

            curs.execute("SELECT telegram_id, status, keywords, telegram_id, parse_mode FROM users")
            users = list(curs.fetchall())

            if not duplicate:
                for user in users:
                    print(user)
                    chat_id = user[0]
                    status = user[1]
                    user_keywords = user[2].split(', ')
                    print(chat_id, status, user_keywords)
                    passed_keywords = []
                    for word in user_keywords:
                        if word in article_keywords:
                            passed_keywords.append(word)
                    print(user[3], web_name)
                    curs.execute("SELECT * FROM user2website WHERE user_id ='{}' and website='{}'".format(user[3], web_name))
                    user2website = curs.fetchone()
                    if user2website:
                        passed_keywords = ', '.join(passed_keywords)
                        print('passed_keywords: ', passed_keywords)
                        print('user2website: ', user2website)
                        if int(status) == 0 and passed_keywords != '' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Знайдено такі ключові слова у наступній статті: ' + passed_keywords + '\n' + new_article['link']), chat_id)
                            curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[3]))
                            conn.commit()
                        elif int(status) == 0 and user2website[3] == '*' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Нова стаття з ' + web_name + '\n' + new_article['link']), chat_id)
                            curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[3]))
                            conn.commit()
    else:
        print("oops, i missed a lot of articles!")
        for new_article_number in range(len(links)-1, -1, -1):
            print(new_article_number)
            new_article = parsed_content[new_article_number]

            #defining article keywords by its header
            title = remove_bad_characters(new_article['title'].split(' '))

            curs.execute("SELECT keywords FROM users")
            keywords_all = list(curs.fetchall())
            keywords_all_new = []
            print('keywords_all',keywords_all)
            for words in keywords_all:
                try:
                    el_list = words[0].split(', ')
                    keywords_all_new = keywords_all_new  + el_list
                except AttributeError:
                    print('error')

            keywords_all = []
            for i in keywords_all_new:
                if i not in keywords_all and i != '':
                    keywords_all.append(i)

            print('all keywords:', keywords_all)
            #end of getting all keywords list, we get keywords_all variable with all of them

            #comparing title words with already existing keywords
            article_keywords = []
            for word in title:
                if word in keywords_all:
                    article_keywords.append(word)

            print('title', title)
            print('keywords in article: ', article_keywords)

            article_keywords = ', '.join(article_keywords)
            print('got an article!')
            try:
                curs.execute("INSERT INTO articles (website_id, url, keywords, parse_time)  VALUES ('{}','{}','{}', '{}')".format(id, new_article['link'], article_keywords, datetime.now().timestamp()))
                conn.commit()
                duplicate = False
                print('article inserted!')
            except psycopg2.IntegrityError:
                print('duplicate')
                duplicate = True
                curs.execute("ROLLBACK")
                conn.commit()

            print('i handled an article!')

            curs.execute("SELECT telegram_id, status, keywords, telegram_id, parse_mode FROM users")
            users = list(curs.fetchall())

            if not duplicate:
                for user in users:
                    chat_id = user[0]
                    status = user[1]
                    user_keywords = user[2].split(', ')
                    print(chat_id, status, user_keywords)
                    passed_keywords = []
                    for word in user_keywords:
                        if word in article_keywords:
                            passed_keywords.append(word)
                    print(user[3], web_name)
                    curs.execute("SELECT * FROM user2website WHERE user_id ='{}' and website='{}'".format(user[3], web_name))
                    user2website = curs.fetchone()
                    if user2website:
                        passed_keywords = ', '.join(passed_keywords)
                        print('passed_keywords: ', passed_keywords)
                        print('user2website: ', user2website)
                        if int(status) == 0 and passed_keywords != '' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Знайдено такі ключові слова у наступній статті: ' + passed_keywords + '\n' + new_article['link']), chat_id)
                            curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[3]))
                            conn.commit()
                        elif int(status) == 0 and user2website[3] == '*' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Нова стаття з ' + web_name + '\n' + new_article['link']), chat_id)
                            curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[3]))
                            conn.commit()
    print('Finished!')


def remove_bad_characters(list):
    list = [s.replace(',', '') for s in list]
    list = [s.replace(' ', '') for s in list]
    list = [s.replace(':', '') for s in list]
    list = [s.replace(";", '') for s in list]
    list = [s.replace('!', '') for s in list]
    list = [s.replace("'", '') for s in list]
    list = [s.replace("[", '') for s in list]
    list = [s.replace("]", '') for s in list]
    list = [s.replace("{", '') for s in list]
    list = [s.replace("}", '') for s in list]
    list = [s.replace("-", '') for s in list]
    list = [s.replace("_", '') for s in list]
    list = [s.replace("=", '') for s in list]
    list = [s.replace("+", '') for s in list]
    list = [s.replace("|", '') for s in list]
    list = [s.replace("(", '') for s in list]
    list = [s.replace(")", '') for s in list]
    list = [s.replace("*", '') for s in list]
    list = [s.lower() for s in list]
    return list



sched = BlockingScheduler()



@sched.scheduled_job('interval', minutes=5)
def timed_job():
    print('This job is run every 5 minutes.')
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('parsing started!'))
    curs.execute("SELECT id FROM websites")
    for website in curs.fetchall():
        parse(website[0])

    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('parsing finished!'))


@sched.scheduled_job('cron', hour='6')
def timed_job2():
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині ранку стартувала!'))
    curs.execute("SELECT * FROM users WHERE parse_mode ='9am'")
    users = curs.fetchall()
    send(users)
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))

@sched.scheduled_job('cron', hour='9')
def timed_job2():
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 12 годині стартувала!'))
    curs.execute("SELECT * FROM users WHERE parse_mode ='12am'")
    users = curs.fetchall()
    send(users)
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))

@sched.scheduled_job('cron', hour='18')
def timed_job2():
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам о 9 годині вечора стартувала!'))
    curs.execute("SELECT * FROM users WHERE parse_mode ='9pm'")
    users = curs.fetchall()
    send(users)
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))

@sched.scheduled_job('cron', hour='4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20')
def timed_job3():
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Розсилка юзерам щогодини стартувала!'))
    curs.execute("SELECT * FROM users WHERE parse_mode ='everyhour'")
    users = curs.fetchall()
    send(users)

    curs.execute("DELETE FROM articles WHERE parse_time < '{}'".format(float(datetime.now().timestamp() - 604800)))
    conn.commit()
    requests.get('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))

def send(users, limit=15, immediate=False):
    from bot import get_json_from_url

    for user in users:
        chat_id = user[1]
        status = user[5]
        user_keywords = user[3].split(', ')
        print(chat_id, status, user_keywords)

        curs.execute("SELECT * FROM user2website WHERE user_id='{}'".format(user[1]))
        websites = curs.fetchall()

        if_nothing = True

        for website in websites:
            curs.execute("SELECT id FROM websites WHERE name='{}'".format(website[2]))
            try:
                web_id = curs.fetchone()[0]
            except TypeError:
                break
            curs.execute("SELECT * FROM articles WHERE parse_time > '{}' and website_id='{}' ORDER BY id DESC".format(float(user[4]), web_id))
            articles = curs.fetchall()

            i=1
            limit=user[13]
            for article in articles:
                if i > limit:
                    break

                passed_keywords = []
                for word in user_keywords:
                    if word in article[3]:
                        passed_keywords.append(word)

                passed_keywords = ', '.join(passed_keywords)
                print('passed_keywords: ', passed_keywords)

                if int(status) == 0 and passed_keywords != '':
                    print(True)
                    get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Я знайшов такі ключові слова у наступній статті: ' + passed_keywords + '\n' + article[2]), user[1])
                    curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[1]))
                    conn.commit()
                    i+=1
                    if_nothing=False
                    time.sleep(0.5)
                elif int(status) == 0 and website[3] == '*':
                    print(True)
                    get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Нова стаття з ' + website[2] + '\n' + article[2]), user[1])
                    curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[1]))
                    conn.commit()
                    i+=1
                    if_nothing=False
                    time.sleep(0.5)

        if if_nothing:
            from bot import send_inline_keyboard

            if immediate:
                send_inline_keyboard([['Обрати інші теми', '/themes'], ['Відібрати інші веб-сайти', '/websites'], ['Переглянути свої ключові слова', '/keywords']], user[1], 'На жаль, останніх новин за твоїми параметрами не знайдено 😔 Зачекай трішки або спробуй наступне:')
            else:
                send_inline_keyboard([['Обрати більше тем', '/themes'], ['Відібрати більше веб-сайтів', '/websites'], ['Переглянути свої ключові слова', '/keywords']], user[1], 'На даний момент свіжих новин за твоїми вказаними параметрами немає 😔 Зачекай ще трішки або спробуй наступне:')






if __name__ == '__main__':
    curs.execute("SELECT id FROM websites")
    for website in curs.fetchall():
        parse(website[0])



    sched.start()
