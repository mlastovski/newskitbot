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
from parsers.bbc import bbc
from parsers.verge import verge
from parsers.guardian import guardian
from parsers.nytimes import nytimes
from parsers.techradar import techradar
from parsers.androidpolice import androidpolice
from parsers.ninetofivemac import ninetofivemac
from parsers.lviv import lviv




os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()


def parse(media, web_name):
    curs.execute("DELETE FROM articles WHERE parse_time < '{}'".format(float(datetime.now().timestamp() - 259200)))
    conn.commit()
    #requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Процес надсилання завершено!'))

    print('media',media)
    from bot import get_json_from_url

    if media == 1:
        try:
            parsed_content = wylsa()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! wylsa'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! wylsa'))
            return None
    elif media == 2:
        try:
            parsed_content = parse_24tvua()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! parse_24tvua'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! parse_24tvua'))
            return None
    elif media == 3:
        try:
            parsed_content = parse_ainua()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! parse_ainua'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! parse_ainua'))
            return None
    elif media == 4:
        try:
            parsed_content = appleinsider()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! appleinsider'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! appleinsider'))
            return None
    elif media == 5:
        try:
            parsed_content = dou()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! dou'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! dou'))
            return None
    elif media == 6:
        try:
            parsed_content = pravda()
        except Exception as e:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! українська правда' + str(e)))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! українська правда' + str(e)))
            return None
    elif media == 7:
        try:
            parsed_content = faktyictv()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! faktyictv'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! faktyictv'))
            return None
    elif media == 8:
        try:
            parsed_content = hromadske()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! hromadske'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! hromadske'))
            return None
    elif media == 9:
        try:
            parsed_content = korrespondent()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! korrespondent'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! korrespondent'))
            return None
    elif media == 10:
        try:
            parsed_content = onehundredtwelve()
        except Exception as e:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! onehundredtwelve'+ str(e)))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! onehundredtwelve'+ str(e)))
            return None
    elif media == 11:
        try:
            parsed_content = isport()
        except Exception as e:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! isport' + str(e)))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! isport' + str(e)))
            return None
    elif media == 12:
        try:
            parsed_content = spiegelDeutsch()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! spiegelDeutsch'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! spiegelDeutsch'))
            return None
    elif media == 13:
        try:
            parsed_content = bbc()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! bbc'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! bbc'))
            return None
    elif media == 14:
        try:
            parsed_content = verge()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! The Verge'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! The Verge'))
            return None
    elif media == 15:
        try:
            parsed_content = guardian()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! The Guardian'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! The Guardian'))
            return None
    elif media == 16:
        try:
            parsed_content = nytimes()
        except Exception as e:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! The NYtimes' + str(e)))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! The NYtimes' + str(e)))
            return None
    elif media == 17:
        try:
            parsed_content = techradar()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! Tech Radar'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! Tech Radar'))
            return None
    elif media == 18:
        try:
            parsed_content = androidpolice()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! Android Police'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! Android Police'))
            return None
    elif media == 19:
        try:
            parsed_content = ninetofivemac()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! 9to5Mac'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! 9to5Mac'))
            return None
    elif media == 20:
        try:
            parsed_content = lviv()
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка парсингу!!!!!! lviv1256'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка парсингу!!!!!! lviv1256'))
            return None
    else:
        return None

    print('Parsing ', web_name)

    id = media
    print('parsed_content',parsed_content)

    if not parsed_content:
        #requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Парсинг сайту ' + str(media) + ' абсолютно не працює'))
        #requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Парсинг сайту ' + str(media) + ' абсолютно не працює'))
        return None

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
                curs.execute("INSERT INTO articles (website_id, url, keywords, parse_time, words)  VALUES ('{}','{}','{}', '{}', '{}')".format(id, new_article['link'], article_keywords, datetime.now().timestamp(), new_article['words']))
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
            article_keywords = article_keywords.split(', ')
            if not duplicate:
                for user in users:
                    print(user)
                    chat_id = user[0]
                    status = user[1]
                    user_keywords = user[2].split(', ')
                    if '' in user_keywords:
                        user_keywords = list(filter(lambda a: a != '', user_keywords))
                    print(chat_id, status, user_keywords)
                    passed_keywords = []
                    for word in user_keywords:
                        if word in article_keywords:
                            passed_keywords.append(word)
                    print(user[3], web_name)
                    curs.execute("SELECT * FROM user2website WHERE user_id ='{}' and website='{}'".format(user[3], media))
                    user2website = curs.fetchone()
                    if user2website:
                        passed_keywords = ', '.join(passed_keywords)
                        print('passed_keywords: ', passed_keywords)
                        print('user2website: ', user2website)
                        if int(status) == 0 and passed_keywords != '' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, passed_keywords + '\n' + new_article['link']), chat_id)
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
                curs.execute("INSERT INTO articles (website_id, url, keywords, parse_time, words)  VALUES ('{}','{}','{}', '{}', '{}')".format(id, new_article['link'], article_keywords, datetime.now().timestamp(), new_article['words']))
                conn.commit()
                duplicate = False
                print('article inserted!')
            except psycopg2.IntegrityError:
                print('duplicate')
                duplicate = True
                curs.execute("ROLLBACK")
                conn.commit()

            print('i handled an article!')

            curs.execute("SELECT telegram_id, status, keywords, telegram_id, parse_mode FROM users WHERE parse_mode='immediate'")
            users = list(curs.fetchall())
            article_keywords = article_keywords.split(', ')
            if not duplicate:
                for user in users:
                    chat_id = user[0]
                    status = user[1]
                    user_keywords = user[2].split(', ')
                    if '' in user_keywords:
                        user_keywords = list(filter(lambda a: a != '', user_keywords))
                    print(chat_id, status, user_keywords)
                    passed_keywords = []
                    for word in user_keywords:
                        if word in article_keywords:
                            passed_keywords.append(word)
                    print(user[3], web_name)
                    curs.execute("SELECT * FROM user2website WHERE user_id ='{}' and website='{}'".format(user[3], media))
                    user2website = curs.fetchone()
                    if user2website:
                        passed_keywords = ', '.join(passed_keywords)
                        print('passed_keywords: ', passed_keywords)
                        print('user2website: ', user2website)
                        if int(status) == 0 and passed_keywords != '' and user[4] == 'immediate':
                            print(True, chat_id)
                            get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, passed_keywords + '\n' + new_article['link']), chat_id)
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
sched2 = BlockingScheduler()



@sched2.scheduled_job('interval', minutes=10)
def timed_job():
    print('This job runs every 5 minutes.')
    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('parsing started!'))
    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('parsing started!'))
    try:
        curs.execute("SELECT * FROM websites")
    except psycopg2.InternalError:
        print('psycopg2.InternalError')
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('psycopg2.InternalError. Trying to fix it...'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('psycopg2.InternalError. Trying to fix it...'))
        time.sleep(10)
        curs.execute("Rollback")
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Rollback done! Now I try one more time!'))
        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Rollback done! Now I try one more time!'))
        try:
            curs.execute("SELECT id FROM websites")
        except psycopg2.InternalError:
            print('psycopg2.InternalError')
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('psycopg2.InternalError. Failed!'))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('psycopg2.InternalError. Failed!'))


    for website in curs.fetchall():
        parse(website[0], website[2])

    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('parsing finished!'))
    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('parsing finished!'))



def send(users, limit=15, immediate=False):
    from bot import get_json_from_url

    now_hour = str(datetime.now().time()).split(':')[0]
    print('now_hour', now_hour)

    for user in users:
        try:
            if user[5] == 1:
                return
            chat_id = user[1]
            status = user[5]
            user_keywords = user[3].split(', ')

            if '' in user_keywords:
                user_keywords = list(filter(lambda a: a != '', user_keywords))

            print(chat_id, status, user_keywords)

            curs.execute("SELECT * FROM user2website WHERE user_id='{}'".format(user[1]))
            websites = curs.fetchall()
            print(websites)
            if_nothing = True
            i=1
            url_send_list=[]
            for website in websites:
                web_id = website[2]
                print('web_id', web_id)
                curs.execute("SELECT * FROM articles WHERE parse_time > '{}' and website_id='{}' ORDER BY id DESC".format(float(user[4]), web_id))
                articles = curs.fetchall()
                print('articles', articles, web_id)

                limit=user[13]
                print('number of limit', limit)
                for article in articles:
                    print(article)
                    print('limit', i)
                    if i > int(limit):
                        print('break!')
                        break

                    passed_keywords = []
                    for word in user_keywords:
                        if word in article[3].split(', ') or word in article[5].split(' '):
                            passed_keywords.append(word)

                    passed_keywords = [i for n, i in enumerate(passed_keywords) if i not in passed_keywords[n + 1:]]  # remove repeating
                    passed_keywords = ', '.join(passed_keywords)
                    print('passed_keywords: ', passed_keywords)


                    if int(status) == 0 and passed_keywords != '' and article[2] not in url_send_list:
                        print(True)
                        if i == 1 and user[7] != 'everyhour' or i == 1 and user[7] == 'everyhour' and now_hour == '05':
                            passed_keywords = 'Твій одноразовий ліміт новин: ' + str(limit) + '. Щоб змінити, скористайся /limit \nЧас отримання новин: '  + str(user[7]) + '. Щоб змінити, скористайся /newstime\n' + passed_keywords
                        get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, passed_keywords + '\n' + article[2]), user[1])
                        curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[1]))
                        conn.commit()
                        i+=1
                        if_nothing=False
                        url_send_list.append(article[2])
                        time.sleep(0.8)
                    elif int(status) == 0 and website[3] == '*' and article[2] not in url_send_list:
                        if i == 1 and user[7] != 'everyhour' or i == 1 and user[7] == 'everyhour' and now_hour == '05':
                            passed_keywords = 'Твій одноразовий ліміт новин: ' + str(limit) + '. Щоб змінити, скористайся /limit \nЧас отримання новин: '  + str(user[7]) + '. Щоб змінити, скористайся /newstime\n' + passed_keywords
                        print(True)
                        get_json_from_url('https://api.telegram.org/bot577877864:AAF5nOap1NlsD6UNHUVHbeMkjNkxHIJo7zE/sendMessage?chat_id={}&text={}'.format(chat_id, 'Нова стаття з ' + website[2] + '\n' + article[2]), user[1])
                        curs.execute("UPDATE users SET send_time ='{}' WHERE telegram_id ='{}'".format(datetime.now().timestamp(), user[1]))
                        conn.commit()
                        i+=1
                        if_nothing=False
                        url_send_list.append(article[2])
                        time.sleep(0.8)
                    elif int(status) == 1:
                        if_nothing=False

            print('Новин надіслано: ', len(url_send_list), '\nСтатті: ',url_send_list)

            from bot import send_inline_keyboard

            if int(status) == 0:
                if if_nothing:
                    if immediate:
                        send_inline_keyboard([['Обрати інші теми', '/themes'], ['Відібрати інші веб-сайти', '/websites'], ['Переглянути свої ключові слова', '/keywords']], user[1], 'На жаль, останніх новин за твоїми параметрами не знайдено 😔 \nЗачекай трішки або спробуй наступне:')
                    else:
                        pass
                        #send_inline_keyboard([['Обрати інші теми', '/themes'], ['Відібрати інші веб-сайти', '/websites'], ['Переглянути свої ключові слова', '/keywords']], user[1], 'На жаль, останніх новин за твоїми параметрами не знайдено 😔 \nЗачекай трішки або спробуй наступне:')
                elif user[7] != 'everyhour':
                    send_inline_keyboard([['Так, дуже!', '/feedbackonce так, все супер'], ['Мені сподобались декілька новин!', '/feedbackonce декілька новин'], ['Було мало корисного((', '/feedbackonce було мало корисного'], ['Маю пропозицію щодо покращення', '/feedback offer']], user[1], 'Чи сподобалась тобі підбірка новин?')
        except Exception as e:
            print('Error_' + str(e))
            curs.execute("Rollback")
            conn.commit()
            from bot import TOKEN
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'ERROR!!! ' + str(e)))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'ERROR!!! ' + str(e)))





if __name__ == '__main__':
    timed_job()
    sched.start()
    sched2.start()

