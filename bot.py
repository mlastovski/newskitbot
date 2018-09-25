# encoding: UTF-8
import json
import requests
import time
from datetime import datetime
import urllib
import psycopg2
import os
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot_add import add_keywords, delete_keywords
from parse import send
from timesend import addnewsheduler

os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()
curs.execute("SELECT value FROM static WHERE id=1")
TOKEN = curs.fetchone()[0]

URL = "https://api.telegram.org/bot{}/".format(TOKEN)

PORT = int(os.environ.get('PORT', '8443'))

TelegramBot = telepot.Bot(TOKEN)



def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url, user_id=None):
    content = get_url(url)
    js = json.loads(content)
    if js['ok'] == False and user_id:
        if js['description'] == 'Forbidden: bot was blocked by the user':
            try:
                print(js)
                print('trying to remove user1 '+ str(user_id))
                curs.execute("SELECT * FROM users WHERE telegram_id='{}'".format(user_id))
                user = curs.fetchone()
                print(user)
                if user:
                    print('trying to remove user2 '+ str(user_id))
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Користувач '+ str(user_id)+' видалив NewsKit, намагаюсь його видалити'))
                    curs.execute("SELECT * FROM users WHERE telegram_id='{}'".format(user_id))
                    user = curs.fetchone()
                    print(user)
                    curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(user_id))
                    websites = ''
                    for i in curs.fetchall():
                        websites = websites + str(i[0]) + ', '

                    curs.execute("INSERT INTO dead_users (telegram_id, first_name, last_name, username, block_date_stamp, block_date_usual, using_days, websites, parse_mode, keywords, themes, language) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(user[1], user[2], user[9], user[10], datetime.now().timestamp(), datetime.now(), (datetime.now().timestamp() - float(user[8]))/86400, websites, user[7], user[3], user[6], user[11]))
                    conn.commit()
                    curs.execute("DELETE FROM users WHERE telegram_id='{}'".format(user_id))
                    curs.execute("DELETE FROM user2website WHERE user_id='{}'".format(user_id))
                    conn.commit()
                    print('bot blocked!' + str(user_id))
                    curs.execute("SELECT id FROM users")
                    users_quan = len(curs.fetchall())
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Користувач ' + user[2] + ' (' + str(user[1]) + ') видалив NewsKit. Загальна кількість активних юзерів: ' + str(users_quan) + str(user)))
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Користувач ' + user[2] + ' (' + str(user[1]) + ') видалив NewsKit. Загальна кількість активних юзерів: ' + str(users_quan)))

                    chat_info = TelegramBot.getChat(user_id)
                    try:
                        last_name = chat_info['last_name']
                    except:
                        last_name = ''

                    try:
                        username = chat_info['username']
                    except:
                        username = ''

                    if not last_name:
                        last_name = ''

                    curs.execute("UPDATE users SET last_name='{}', username='{}' WHERE telegram_id='{}'".format(last_name, username, user_id))
                    conn.commit()

                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'надіслано з сенд кіборд'))
                else:
                    print('bot was blocked by user! user already deleted!')
            except:
                print('bot was blocked by user!')
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def define(text, id):
    curs = conn.cursor()
    curs.execute("SELECT * FROM system ORDER BY id")
    system = curs.fetchall()

    if_passed = False

    curs.execute("SELECT command FROM users WHERE telegram_id='{}'".format(id))
    command = curs.fetchone()
    print('comm', command)

    try:
        command = command[0]
    except TypeError:
        command=''

    if command != '':
        if text == '/cancel':
            action = '/cancel'
        else:
            action = command
            text = [text]
    else:
        text = text.lower()

        for line in range(0, len(system)):
            for expression in system[line][2].split(', '):
                print('passed loop: ', line, expression)
                if text.startswith(expression):
                    curs.execute("SELECT action FROM system WHERE id = '{}'".format(int(line) + 1))
                    action = curs.fetchone()[0]
                    print(action)
                    if action == 'feedback' or action == 'toallusers':
                        text = text.split()
                        del text[:len(expression.split(' '))]
                        text = [' '.join(text)]
                        if_passed = True
                        break
                    elif action == 'touser':
                        text = text.split()
                        id = text[1]
                        del text[:2]
                        text = [id, ' '.join(text)]
                        print(text)
                        if_passed = True
                        break

                    # now we know what action it is
                    print(True)
                    if_passed = True

                    # let`s extract command from the text
                    text = replace(text, [(',', ' і '), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                                          ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''),
                                          ("(", ''), (")", ''), ("*", ''), ("з моїх ключових слів", ''),
                                          ("до моїх ключових слів", ''), ("до списку новин", ''), ("в мою базу даних", ''),
                                          ("мені", ''), ("пліз слова", ''), ("пліз слово", ''), ("пліз", ''),
                                          ("ключові слова", '')])
                    text = text.split()
                    print('text before', text)
                    del text[:len(expression.split(' '))]
                    text = ' '.join(text)
                    text = replace(text, [(' і ', ';'), (' й ', ';'), (' та ', ';'), (';;', ';')])
                    text = text.split(';')
                    text = replace(text,
                                   [(',', ''), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                                    ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''), ("(", ''),
                                    (")", ''), ("*", '')])
                    print('text', text)

                    break

            if if_passed:
                print('line', line)
                break
            elif not if_passed and line == len(system) - 1:  # if it`s the last iteration and line still isn`t found
                line = 'nomatch'
                action = 'nomatch'
                break


        print('line', line, action, text)

    return {'action': action, 'text': text}


def replace(var, list_from_to):
    for str_from, str_to in list_from_to:
        print('replace', str_from, str_to)
        if isinstance(var, str):
            var = var.replace(str_from, str_to)
        elif isinstance(var, list):
            list_new = []
            for word in var:
                word = word.replace(str_from, str_to)
                list_new.append(word)
            var = list_new
        print('var', var)

    return var


def echo_all(updates):
    print(updates)
    for update in updates["result"]:
        try:
            chat = update["message"]["chat"]["id"]
            id = update["message"]['chat']['id']
            name = update["message"]['chat']['first_name']
            try:
                last_name = update["message"]['chat']['last_name']
            except KeyError:
                last_name = ''
            try:
                username = update["message"]['chat']['username']
            except KeyError:
                username = ''
            text = update["message"]["text"]
            mess_id=None
        except KeyError:
            try:
                text = update["callback_query"]["data"]

                chat = update["callback_query"]["from"]["id"]
                id = update["callback_query"]["from"]["id"]
                mess_id = update["callback_query"]["message"]['message_id']
                name = update["callback_query"]['from']['first_name']
                try:
                    last_name = update["callback_query"]['from']['last_name']
                except KeyError:
                    last_name = ''
                try:
                    username = update["message"]['chat']['username']
                except KeyError:
                    username = ''
            except KeyError:
                text = 'На жаль, я не підтримую такий формат повідомлення!'


        print(chat, text, name)

        result = define(text, id)
        action = result['action']
        text = result['text']

        curs = conn.cursor()

        if action == 'start':
            # text = str([update['message']['chat']['id'], update['message']['chat']['first_name']])
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            user = curs.fetchone()
            if not user:
                curs.execute(
                    "INSERT INTO users (telegram_id, name, keywords, send_time, status, register_date, last_name, username) VALUES ('{}', '{}', '', '{}', 0, '{}', '{}', '{}')".format(
                        id, name, datetime.now().timestamp() - 86400, datetime.now().timestamp(), last_name, username))
                # send_message('Ти успішно записаний в базу даних!', chat)
                conn.commit()
                send_inline_keyboard([['Українська 🇺🇦', '/start ua'], ['Русский 🇷🇺', '/start ru'],
                                      ['English 🇬🇧', '/start en']], chat, 'Привіт! Обери, будь ласка, мову 🙂\n \n Привет! Выбери, пожалуйста, язык 🙂 \n \n Hi! Choose your language please 🙂')

                curs.execute("SELECT id FROM users")
                users_quan = len(curs.fetchall())
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Новий користувач ' + name + ' ' + last_name + ' (' + str(id) + '). Загальна кількість активних юзерів: ' + str(users_quan)))
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Новий користувач ' + name + ' ' + last_name + ' (' + str(id) + '). Загальна кількість активних юзерів: ' + str(users_quan)))
            else:
                print(text[0])
                #send_help(text, chat)
                if text[0] == 'ru':
                    curs.execute("UPDATE users SET language='ru' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    send_inline_keyboard([['Продолжить на украинском', '/start ua']], chat, 'К сожалению, я ещё не умею хорошо общаться на русском(( Но ты можеш продолжить на украинском)) Русская версия появиться совсем скоро и мы тебе обязательно о ней сообщим!')

                elif text[0] == 'en':
                    curs.execute("UPDATE users SET language='en' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    send_inline_keyboard([['Continue in Ukrainian', '/start ua']], chat, "Unfortunately, I don't support English version yet(( But you can continue using Ukrainian one)) English language appears soon and we'll notify you")
                else:
                    curs.execute("UPDATE users SET language='ua' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    send_message('Тебе вітає NewsKit!', chat)
                    # send_message('Я - чат-бот, який надсилатиме тобі підбірку свіжих персоналізованих новин у зручний час з обраних новинних веб-сайтів.', chat)
                    send_inline_keyboard([['Обрати цікаві теми', '/themes newskit']], chat, 'Я - чат-бот, який надсилатиме тобі підбірку свіжих персоналізованих новин у зручний час з обраних новинних веб-сайтів.')

                # send_inline_keyboard([['Обрати цікаві мені теми', '/themes newskit']], chat, 'Тебе вітає NewsKit! \n Я - чат-бот, який надсилатиме тобі підбірку свіжих персоналізованих новин у зручний час з обраних новинних веб-сайтів.')
        elif action == 'viewkeywords':
            curs = conn.cursor()
            curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}'".format(id))
            # send_message('Твій список ключових слів: ' + curs.fetchone()[0], chat)
            words = curs.fetchone()[0]
            print(words, id, name)
            send_inline_keyboard([['Отримати останні новини', '/getlastnews'], ['Більше про мої можливості', '/help']], chat, 'Твій список ключових слів: ' + str(words))
        elif action == 'addkeywords':
            curs = conn.cursor()
            curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            try:
                print('user', id, name)
                present_words = curs.fetchone()[0]
            except TypeError:
                present_words = ''
            present_words_list = present_words.split(', ')
            present_words_list = replace(present_words_list,
                                         [(',', ''), (' ', ''), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''),
                                          ("]", ''), ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''),
                                          ("|", ''), ("(", ''), (")", ''), ("*", '')])

            text = replace(text,
                           [(',', ''), (' ', ''), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                            ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''), ("(", ''),
                            (")", ''), ("*", '')])
            print(text)
            # text consists of received list of new keywords

            # loop for detecting repeating keywords
            isgoingtoberemoved = []
            for word in text:
                if word in present_words_list:
                    send_message(str(word + ' не додано через повтор'), chat)
                    isgoingtoberemoved.append(word)
                else:
                    send_message(str(word + ' додано'), chat)

            # loop for removing this repeating elements
            for repeated in isgoingtoberemoved:
                text.remove(repeated)

            if len(text) != 0:
                text = ', '.join(text)
            else:
                text = ''.join(text)
            # send_message(present_words_list, chat)
            if len(present_words_list) == 1 and present_words_list[0] == '':
                present_words_list = ''.join(present_words_list)
            else:
                present_words_list = ', '.join(present_words_list)
                if text != '':
                    present_words_list = present_words_list + ', '

            if present_words != '':
                present_words = present_words + ', '
            curs.execute("UPDATE users SET keywords ='{}' WHERE telegram_id ='{}' AND name ='{}'".format(
                str(present_words_list + text), id, name))
            conn.commit()
            send_message('Ваш список ключових слів: ' + str(present_words_list + text), chat)
        elif action == 'deletekeywords':
            text = replace(text,
                           [(',', ''), (' ', ''), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                            ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''), ("(", ''),
                            (")", ''), ("*", '')])
            print('text', text)
            curs = conn.cursor()
            curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            present_words = curs.fetchone()[0]
            present_words_list = present_words.split(', ')
            present_words_list = replace(present_words_list,
                                         [(',', ''), (' ', ''), (':', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''),
                                          ("]", ''), ("{", ''), ("}", ''), ("-", ''), ("_", ''), ("=", ''), ("+", ''),
                                          ("|", ''), ("(", ''), (")", ''), ("*", '')])

            # loop for removing chosen elements
            for should_remove in text:
                if should_remove in present_words_list:
                    present_words_list.remove(should_remove)
                    send_message(str(should_remove + ' вилучено'), chat)
                else:
                    send_message(str(should_remove + ' не є твоїм ключовим словом'), chat)

            if len(present_words_list) == 1 and present_words_list[0] == '':
                present_words_list = ''.join(present_words_list)
            else:
                present_words_list = ', '.join(present_words_list)

            curs.execute(
                "UPDATE users SET keywords ='{}' WHERE telegram_id ='{}' AND name ='{}'".format(str(present_words_list),
                                                                                                id, name))
            conn.commit()
            send_message('Ваш список ключових слів: ' + str(present_words_list), chat)

        elif action == 'deleteaccount':
            curs = conn.cursor()
            curs.execute("DELETE FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            conn.commit()

            text = 'Ти більше не отримуватимеш щоденних розсилок(( Щоб відновити цю можливість напиши мені /start'
            send_message(text, chat)
        elif action == 'stop':
            curs = conn.cursor()
            curs.execute("SELECT status FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            status = int(curs.fetchone()[0])
            if status != 1:
                curs.execute("UPDATE users SET status = 1 WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
                conn.commit()
                text = 'Ти більше не отримуватимеш щоденних розсилок(( Щоб відновити цю можливість напиши мені /renew'
            else:
                text = 'Ви вже відмовились від отримання новин раніше(( Щоб відновити цю можливість напиши мені /renew'

            send_message(text, chat)

        elif action == 'renew':
            curs = conn.cursor()
            curs.execute("SELECT status FROM users WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
            status = int(curs.fetchone()[0])
            if status != 0:
                curs.execute("UPDATE users SET status = 0 WHERE telegram_id ='{}' AND name ='{}'".format(id, name))
                conn.commit()
                text = 'Ти знову зі мною! Тепер ти отримуватимеш щоденну підбірку персоналізованих новин!'
            else:
                text = 'Ви вже погодились на отримання новин раніше! Дякую за довіру!'

            send_message(text, chat)
        elif action == 'choose_themes':
            curs = conn.cursor()

            curs.execute("SELECT theme FROM themes")
            words=[]
            for theme in curs.fetchall():
                words.append(theme[0])

            curs.execute("SELECT themes FROM users WHERE telegram_id ='{}'".format(id))
            themes = curs.fetchone()[0].split(', ')
            print(words, themes)

            if text[0] == 'newskit':
                markup = send_choose(words, themes, text, 'theme', True)
            else:
                markup = send_choose(words, themes, text, 'theme')

            send_inline_keyboard(markup, chat, "Обери цікаву тобі тематику новин! Ця операція є обов'язковою, адже без жодної обраної теми новини надсилатись не будуть. ")
        elif action == 'chosentheme':
            try:
                mode = text[1]
            except IndexError:
                mode = None

            curs.execute("SELECT theme FROM themes")
            words=[]
            for theme in curs.fetchall():
                words.append(theme[0])

            curs.execute("SELECT themes FROM users WHERE telegram_id ='{}'".format(id))
            themes = curs.fetchone()[0].split(', ')
            print(words, themes)

            #filtring from empties
            if ' ' in themes:
                themes.remove(' ')
            elif '' in themes:
                themes.remove('')

            if text[0] in themes:
                themes.remove(text[0])
                db_action = 'delete'
            else:
                themes.append(text[0])
                db_action = 'add'
            print(themes)
            markup = []
            i = 1
            for word in words:
                word_filtered = ''.join(replace(list(word),[("'", '')]))
                if word_filtered in themes:
                    word_new = '✅' + word
                else:
                    word_new = word
                if i%2==1:
                    if mode:
                        markup.append([word_new, '/chosentheme ' + word + ' і forward'])
                    else:
                        markup.append([word_new, '/chosentheme ' + word])
                else:
                    if mode:
                        markup.append([word_new, '/chosentheme ' + word + ' і forward', 'continue'])
                    else:
                        markup.append([word_new, '/chosentheme ' + word, 'continue'])
                i+=1
            print(markup)
            #send_inline_keyboard(markup, chat, 'Обери цікаві тобі теми))')
            reply_markup = get_reply_markup(markup, 'theme', mode)
            if mess_id:
                try:
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Обери цікаву тобі тематику новин! Ця операція є обов\'язковою, адже без жодної обраної теми новини надсилатись не будуть.', reply_markup=reply_markup)
                except telepot.exception.TelegramError:
                    send_inline_keyboard(markup, chat, 'Обери цікаву тобі тематику новин! Ця операція є обов\'язковою, адже без жодної обраної теми новини надсилатись не будуть.')
            else:
                send_inline_keyboard(markup, chat, 'Обери цікаву тобі тематику новин! Ця операція є обов\'язковою, адже без жодної обраної теми новини надсилатись не будуть.')
            curs.execute("UPDATE users SET themes='{}' WHERE telegram_id = '{}'".format(', '.join(themes)+', ', id))
            conn.commit()

            print(text[0])

            curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
            chosen_languages= curs.fetchone()[0].split(', ')
            print('chosen_languages', chosen_languages)
            curs.execute("SELECT * FROM themes WHERE theme ='{}'".format(text[0]))
            keywords_theme = curs.fetchall()[0]
            keywords_final = ''
            if 'ua' in chosen_languages:
                print('ua')
                keywords_final = keywords_final + keywords_theme[2] + ', '
            if 'ru' in chosen_languages:
                print('ru')
                keywords_final = keywords_final + keywords_theme[3] + ', '
            if 'en' in chosen_languages:
                print('en')
                keywords_final = keywords_final + keywords_theme[4] + ', '
            if 'de' in chosen_languages:
                print('de')
                keywords_final = keywords_final + keywords_theme[5] + ', '

            print(keywords_final)

            if db_action == 'delete':
                text = keywords_final.split(', ')
                delete_keywords(conn, id, name, text, chat)
            else:
                text = keywords_final.split(', ')
                add_keywords(conn, id, name, text, chat)

        elif action == 'websites':
            try:
                mode = text[1]
            except IndexError:
                mode = None

            curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
            chosen_languages= curs.fetchone()[0].split(', ')

            curs.execute("SELECT * FROM websites" )
            fetchall = curs.fetchall()
            websites=[]
            print(fetchall)
            for website in fetchall:
                if website[3] in chosen_languages:
                    websites.append(website[2])
            print('websites', websites)
            curs.execute("SELECT website FROM user2website WHERE user_id ='{}'".format(id))
            chosen_websites=[]
            for website in curs.fetchall():
                chosen_websites.append(website[0])
            print(websites, chosen_websites)
            # now we have 2 vars: websites - list of all supported websites and chosen_websites - list of chosen websites
            if text[0] == 'newskit':
                markup = send_choose(websites, chosen_websites, text, 'website', True)
            else:
                markup = send_choose(websites, chosen_websites, text, 'website')

            send_inline_keyboard(markup, chat, 'Обери цікаві тобі веб-сайти! З них тобі будуть надсилатися персоналізовані новини 😉')
        elif action == 'chosenwebsite':
            try:
                mode = text[1]
            except IndexError:
                mode = None
            print('mode', mode)

            curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
            chosen_languages= curs.fetchone()[0].split(', ')

            curs.execute("SELECT * FROM websites" )
            fetchall = curs.fetchall()
            websites=[]
            print(fetchall)
            for website in fetchall:
                if website[3] in chosen_languages:
                    websites.append(website[2])
            print('websites', websites)

            curs.execute("SELECT website FROM user2website WHERE user_id ='{}'".format(id))
            chosen_websites=[]
            for website in curs.fetchall():
                chosen_websites.append(website[0])
            print(websites, chosen_websites)

            #filtring from empties
            if ' ' in chosen_websites:
                chosen_websites.remove(' ')
            elif '' in chosen_websites:
                chosen_websites.remove('')

            if text[0] in chosen_websites:
                chosen_websites.remove(text[0])
                db_action = 'delete'
            else:
                chosen_websites.append(text[0])
                db_action = 'add'
            print(chosen_websites)
            markup = []
            i = 1
            for website in websites:
                website_filtered = ''.join(replace(list(website),[("'", '')]))
                if website_filtered in chosen_websites:
                    word_new = '✅' + website
                else:
                    word_new = website
                if i%2==1:
                    if mode:
                        markup.append([word_new, '/chosenwebsite ' + website + ' і forward'])
                    else:
                        markup.append([word_new, '/chosenwebsite ' + website])
                else:
                    if mode:
                        markup.append([word_new, '/chosenwebsite ' + website + ' і forward', 'continue'])
                    else:
                        markup.append([word_new, '/chosenwebsite ' + website, 'continue'])
                i+=1
            print(markup)
            #send_inline_keyboard(markup, chat, 'Обери цікаві тобі теми))')
            reply_markup = get_reply_markup(markup, 'website', mode)
            print('reply_markup', reply_markup)
            if mess_id:
                try:
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Обери цікаві тобі веб-сайти! З них тобі будуть надсилатися персоналізовані новини 😉', reply_markup=reply_markup)
                except telepot.exception.TelegramError:
                    send_inline_keyboard(markup, chat, 'Обери цікаві тобі веб-сайти! З них тобі будуть надсилатися персоналізовані новини 😉')
            else:
                send_inline_keyboard(markup, chat, 'Обери цікаві тобі веб-сайти! З них тобі будуть надсилатися персоналізовані новини 😉')

            print(text[0])
            if db_action == 'delete':
                curs.execute("DELETE FROM user2website WHERE website ='{}' and user_id ='{}'".format(text[0], id))
                conn.commit()
            else:
                curs.execute("INSERT INTO user2website (website, user_id) VALUES ('{}', '{}')".format(text[0], id))
                conn.commit()
        elif action == 'setnewstime':
            if text[0] != '':
                mode = text[0]
                phrase = ' і forward'
            else:
                mode = None
                phrase = ''

            curs.execute("SELECT parse_mode FROM users WHERE telegram_id ='{}'".format(id))
            parse_mode = curs.fetchone()[0]

            parse_possible = ['immediate', '9am', 'everyhour', '12am', '9pm']
            parse_all = [['Одразу', '/chosentime immediate'], ['О 12 годині', '/chosentime 12am', 'continue'] ,['Щогодини протягом дня', '/chosentime everyhour'],
                                      ['О 9 ранку', '/chosentime 9am'], ['0 9 вечора', '/chosentime 9pm', 'continue']]
            markup = []
            i = 1
            for parse in parse_all:
                btn_name = parse[0]
                btn_action = parse[1].split()[1]
                print('nums',i, i%10)
                if parse_mode == btn_action:
                    if i%10!=1 and i%10==2 and i%10!=4 or i%10!=1 and i%10!=4 and i%10==5:
                        new = ['✅' + btn_name, '/chosentime ' + btn_action + phrase, 'continue']
                    else:
                        print('here 3')
                        new = ['✅' + btn_name, '/chosentime ' + btn_action + phrase]
                else:
                    if i%10!=1 and i%10==2 and i%10!=4 or i%10!=1 and i%10!=4 and i%10==5:
                        new = [btn_name, '/chosentime ' + btn_action + phrase, 'continue']
                    else:
                        print('here 3')
                        new = [btn_name, '/chosentime ' + btn_action + phrase]
                i+=1
                markup.append(new)

            if text[0] == 'newskit':
                markup.append(['Далі ➡️', '/endtour'])

            send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини?')
        elif action == 'news_language':
            try:
                mode = text[1]
            except IndexError:
                mode = None

            curs.execute("SELECT language FROM websites")
            ua, ru, en, de = 0, 0, 0, 0
            for i in curs.fetchall():
                if i[0] == 'ua':
                    ua += 1
                elif i[0] == 'ru':
                    ru += 1
                elif i[0] == 'en':
                    en += 1
                elif i[0] == 'de':
                    de += 1
            print(ua, ru, en, de)

            languages=['Українська (' + str(ua) + ')', 'Російська (' + str(ru) + ')', 'Англійська (' + str(en) + ')', 'Німецька (' + str(de) + ')']


            curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
            chosen_languages=[]
            for lang in curs.fetchone()[0].split(', '):
                if lang == 'ua':
                    chosen_languages.append('Українська (' + str(ua) + ')')
                elif lang == 'ru':
                    chosen_languages.append('Російська (' + str(ru) + ')')
                elif lang == 'en':
                    chosen_languages.append('Англійська (' + str(en) + ')')
                elif lang == 'de':
                    chosen_languages.append('Німецька (' + str(de) + ')')


            print(languages, chosen_languages)
            # now we have 2 vars: websites - list of all supported websites and chosen_websites - list of chosen websites
            if text[0] == 'newskit':
                markup = send_choose(languages, chosen_languages, text, '_news_language', True)
            else:
                markup = send_choose(languages, chosen_languages, text, '_news_language')

            send_inline_keyboard(markup, chat, 'Обери мову новин! Від мови залежать веб-сайти, на які ти зможеш підписатися! (їх кількість вказана в дужках)')
        elif action == 'chosen_language':
            try:
                mode = text[1]
                mode = True
            except IndexError:
                mode = False
            print('mode', mode)

            curs.execute("SELECT language FROM websites")
            ua, ru, en, de = 0, 0, 0, 0
            for i in curs.fetchall():
                if i[0] == 'ua':
                    ua += 1
                elif i[0] == 'ru':
                    ru += 1
                elif i[0] == 'en':
                    en += 1
                elif i[0] == 'de':
                    de += 1
            print(ua, ru, en, de)

            languages=['Українська (' + str(ua) + ')', 'Російська (' + str(ru) + ')', 'Англійська (' + str(en) + ')', 'Німецька (' + str(de) + ')']

            curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
            chosen_languages=[]
            for lang in curs.fetchone()[0].split(', '):
                if lang == 'ua':
                    chosen_languages.append('українська')
                elif lang == 'ru':
                    chosen_languages.append('російська')
                elif lang == 'en':
                    chosen_languages.append('англійська')
                elif lang == 'de':
                    chosen_languages.append('німецька')

            print(languages, chosen_languages, text[0].split()[0])

            if text[0].split()[0] in chosen_languages:
                chosen_languages.remove(text[0].split()[0])
                db_action = 'delete'
            else:
                chosen_languages.append(text[0].split()[0])
                db_action = 'add'
            print(chosen_languages)

            chosen_languages2 = []
            for makebetter in chosen_languages:
                if makebetter == 'українська':
                    chosen_languages2.append('Українська (' + str(ua) + ')')
                elif makebetter == 'російська':
                    chosen_languages2.append('Російська (' + str(ru) + ')')
                elif makebetter == 'англійська':
                    chosen_languages2.append('Англійська (' + str(en) + ')')
                elif makebetter == 'німецька':
                    chosen_languages2.append('Німецька (' + str(de) + ')')


            markup = []
            i = 1
            for language in languages:
                filtered = ''.join(replace(list(language),[("'", '')]))
                if filtered in chosen_languages2:
                    word_new = '✅' + language
                else:
                    word_new = language
                if i%2==1:
                    if mode:
                        markup.append([word_new, '/chosen_news_language ' + language + ' і forward'])
                    else:
                        markup.append([word_new, '/chosen_news_language ' + language])
                else:
                    if mode:
                        markup.append([word_new, '/chosen_news_language ' + language + ' і forward', 'continue'])
                    else:
                        markup.append([word_new, '/chosen_news_language ' + language, 'continue'])
                i+=1
            print(markup)
            #send_inline_keyboard(markup, chat, 'Обери цікаві тобі теми))')
            reply_markup = get_reply_markup(markup, '_news_language', mode)
            print('reply_markup', reply_markup)
            if mess_id:
                try:
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Обери мову новин! Від мови залежать веб-сайти, на які ти зможеш підписатися! (їх кількість вказана в дужках)', reply_markup=reply_markup)
                except telepot.exception.TelegramError:
                    send_inline_keyboard(markup, chat, 'Обери мову новин! Від мови залежать веб-сайти, на які ти зможеш підписатися! (їх кількість вказана в дужках)')
            else:
                send_inline_keyboard(markup, chat, 'Обери мову новин! Від мови залежать веб-сайти, на які ти зможеш підписатися! (їх кількість вказана в дужках)')

            print('passed_lang', text[0], chosen_languages)
            db_languages = []
            for i in chosen_languages:
                if i == 'українська':
                    db_languages.append('ua')
                elif i == 'російська':
                    db_languages.append('ru')
                elif i == 'англійська':
                    db_languages.append('en')
                elif i == 'німецька':
                    db_languages.append('de')

            curs.execute("SELECT themes FROM users WHERE telegram_id ='{}'".format(id))
            themes = curs.fetchall()
            print('themes', themes[0][0])
            curs.execute("SELECT * FROM themes WHERE theme IN {}".format(tuple(themes[0][0].split(', '))))
            keywords_theme = curs.fetchall()
            print('keywords_theme', keywords_theme)
            keywords_final = ''
            choose = text[0].split()[0]
            for theme_line in keywords_theme:
                if choose == 'українська':
                    keywords_final = keywords_final + theme_line[2]
                elif choose == 'російська':
                    keywords_final = keywords_final + theme_line[3]
                elif choose == 'англійська':
                    keywords_final = keywords_final + theme_line[4]
                elif choose == 'німецька':
                    keywords_final = keywords_final + theme_line[5]

                keywords_final = keywords_final + ', '

            print(keywords_final)

            if db_action == 'delete':
                keywords_final = keywords_final.split(', ')
                print(keywords_final)
                delete_keywords(conn, id, name, keywords_final, chat)
            else:
                keywords_final = keywords_final.split(', ')
                add_keywords(conn, id, name, keywords_final, chat)

            print(db_languages)
            curs.execute("UPDATE users SET news_language='{}' WHERE telegram_id='{}'".format(', '.join(db_languages), id))
            conn.commit()
        elif action == 'chosentime':
            try:
                mode = text[1]
                phrase = ' і forward'
            except IndexError:
                mode = None
                phrase = ''

            parse_mode = text[0]

            curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id ='{}'".format(parse_mode, id))
            conn.commit()

            parse_possible = ['immediate', '9am', 'everyhour', '12am', '9pm']
            parse_all = [['Одразу', '/chosentime immediate'], ['О 12 годині', '/chosentime 12am', 'continue'] ,['Щогодини протягом дня', '/chosentime everyhour'],
                                      ['О 9 ранку', '/chosentime 9am'], ['0 9 вечора', '/chosentime 9pm', 'continue']]
            markup = []
            i = 1
            for parse in parse_all:
                btn_name = parse[0]
                btn_action = parse[1].split()[1]
                print('nums',i, i%10)
                if parse_mode == btn_action:
                    if i%10!=1 and i%10==2 and i%10!=4 or i%10!=1 and i%10!=4 and i%10==5:
                        new = ['✅' + btn_name, '/chosentime ' + btn_action + phrase, 'continue']
                    else:
                        print('here 3')
                        new = ['✅' + btn_name, '/chosentime ' + btn_action + phrase]
                else:
                    if i%10!=1 and i%10==2 and i%10!=4 or i%10!=1 and i%10!=4 and i%10==5:
                        new = [btn_name, '/chosentime ' + btn_action + phrase, 'continue']
                    else:
                        print('here 3')
                        new = [btn_name, '/chosentime ' + btn_action + phrase]
                i+=1
                markup.append(new)

            reply_markup = get_reply_markup(markup, 'time', mode)
            print('hereherehere')
            TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Коли ти хочеш отримувати новини?', reply_markup=reply_markup)
            if mess_id:
                try:
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Коли ти хочеш отримувати новини?', reply_markup=reply_markup)
                except telepot.exception.TelegramError:
                    pass
                    #send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини?')
            else:
                send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини?')

        elif action == 'endtour':

            send_inline_keyboard([['Більше про мої можливості', '/help'], ['Отримати останні новини!', '/getlastnews']], chat, 'Ура! Відтепер ми з тобою найкращі друзі! Я тобі надсилатиму новини за всіма критеріями, які ти мені вказав ☺️☺️☺️')
        elif action == 'chooseall':
            if text[0] != '':
                curs.execute("SELECT keywords FROM user2website WHERE website ='{}' and user_id ='{}'".format(text[0], id))
                try:
                    keywords = curs.fetchone()[0]
                except TypeError:
                    return
                if keywords  == '':
                    curs.execute("UPDATE user2website SET keywords='*' WHERE website ='{}' and user_id ='{}'".format(text[0], id))
                else:
                    curs.execute("UPDATE user2website SET keywords='' WHERE website ='{}' and user_id ='{}'".format(text[0], id))
                conn.commit()

                curs.execute("SELECT website FROM user2website WHERE keywords ='*' and user_id ='{}'".format(id))
                websites = []
                for i in curs.fetchall():
                    websites.append(i[0])
                print(websites)

                curs.execute("SELECT name FROM websites")
                markup=[]
                for website in curs.fetchall():
                    if website[0] in websites:
                        markup.append(['▶️' + website[0] + '◀️', '/chooseall ' + website[0]])
                    else:
                        markup.append([website[0], '/chooseall ' + website[0]])

                reply_markup = get_reply_markup(markup)

                if mess_id:
                    try:
                        TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️', reply_markup=reply_markup)
                    except telepot.exception.TelegramError:
                        send_inline_keyboard(markup, chat, 'Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️')
                else:
                    send_inline_keyboard(markup, chat, 'Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️')
            else:
                curs.execute("SELECT website FROM user2website WHERE keywords ='*' and user_id ='{}'".format(id))
                websites = []
                for i in curs.fetchall():
                    websites.append(i[0])
                print(websites)

                curs.execute("SELECT name FROM websites")
                markup=[]
                for website in curs.fetchall():
                    if website[0] in websites:
                        markup.append(['▶️' + website[0] + '◀️', '/chooseall ' + website[0]])
                    else:
                        markup.append([website[0], '/chooseall ' + website[0]])

                send_inline_keyboard(markup, chat, 'Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️')
        elif action == 'getlastnews':
            curs.execute("SELECT * FROM users WHERE telegram_id ='{}'".format(id))
            user_current = list(curs.fetchone())

            if user_current[8] == user_current[4]: #if user first registered and needs news
                user_current[4] = 1 #this is needed for getting news ever since. (last send date is set to 1)
                print(user_current)
                send([user_current], 7, True)
            else:
                send([user_current], immediate=True)
        elif action == 'newstime':
            if len(text[0]) == 0:
                curs.execute("UPDATE users SET command='newstime' WHERE telegram_id='{}'".format(id))
                conn.commit()
                send_message('Надішли мені час, коли ти хочеш отримувати новини. Дотримуйся такого формату: \n 10:47 \n /cancel, щоб скасувати', id)
            else:
                print(text[0])

                try:
                    hours=int(text[0].split(':')[0])
                    minutes=int(text[0].split(':')[1])
                    print(hours, minutes)
                    if hours < 24 and hours >= 0 and minutes < 60 and minutes >= 0 or hours == 24 and minutes == 0:
                        print('here')
                        if int(hours) > 3:
                            hours = int(hours) - 3
                        elif int(hours) == 2:
                            hours = 23
                        elif int(hours) == 1:
                            hours = 22
                        elif int(hours) == 24:
                            hours = 21

                        if int(hours) < 10:
                            hours = '0' + str(hours)
                        if int(minutes) < 10:
                            minutes = '0' + str(minutes)

                        print(hours, minutes)
                        addnewsheduler(str(hours), minutes, id)
                        send_message('Час встановлено!', id)
                    else:
                        send_message('Час не підходить. Напиши час у форматі ГГ:ХХ. Наприклад, 09:21. Спробуй ще раз! /newstime', id)
                    curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                except ValueError:
                    send_message('Час не підходить. Напиши час у форматі ГГ:ХХ. Наприклад, 09:21. Спробуй ще раз! \nЩоб скасувати, натисни /cancel', id)

        elif action == 'feedback':
            print(text)
            if len(text[0]) == 0:
                curs.execute("UPDATE users SET command='feedback' WHERE telegram_id='{}'".format(id))
                conn.commit()
                send_message('Надішли мені фідбек наступним повідомленням! /cancel, щоб скасувати', id)
            else:
                curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                conn.commit()
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                send_message('Я надіслав твій фідбек!', chat)
        elif action == 'feedbackonce':
            print(text)
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
            send_message('Дякую за відповідь! Вона дуже важлива для мене!', chat)
        elif action == '/cancel':
            curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
            conn.commit()
            send_message('Скасовано!', id)
        elif action == 'touser':
            if id == 138918380 or id == 373407132:
                if len(text) < 2:
                    send_message('Неправильно!', chat)
                else:
                    print(True)
                    get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, text[0], 'Відповідь на твій фідбек: \n' + str(text[1])), text[0])
                    send_message('Надіслано!', chat)
            else:
                send_message('Хмммм! Для розсилки юзерам треба мати вищий пропуск! Ти його, на жаль, не маєш(( Проте не засмучуйся)) Напиши /getlastnews і я потішу тебе останніми новинами!', chat)
        elif action == 'toallusers':
            if id == 138918380 or id == 373407132:
                print(True)
                curs.execute("SELECT telegram_id FROM users")
                users = curs.fetchall()
                print(len(users))
                send_message('Масову розсилку розпочато!', chat)
                for i in users:
                    print(i[0], text[0])
                    get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, i[0], str(text[0])), i[0])
                send_message('Повідомлення успішно розіслано всім користувачам!', chat)
            else:
                send_message('Хмммм! Для розсилки всім юзерам треба мати вищий пропуск! Ти його, на жаль, не маєш(( Проте не засмучуйся)) Напиши /getlastnews і я потішу тебе останніми новинами!', chat)
        elif action == 'aboutuser':
            print(text)
            if id == 138918380 or id == 373407132:
                if len(text) < 1:
                    send_message('Неправильно!', chat)
                else:
                    print(True)
                    curs.execute("SELECT * FROM users WHERE telegram_id = '{}'".format(text[0]))
                    user = curs.fetchone()
                    send_message(str(user), chat)
            else:
                send_message('Хмммм! Для розсилки юзерам треба мати вищий пропуск! Ти його, на жаль, не маєш(( Проте не засмучуйся)) Напиши /getlastnews і я потішу тебе останніми новинами!', chat)

        elif action == 'statistic':
            curs.execute("SELECT telegram_id FROM users")
            users = curs.fetchall()
            subscribed = len(users)
            curs.execute("SELECT telegram_id FROM dead_users")
            users = curs.fetchall()
            unsubscribed = len(users)
            send_message('Підписаних юзерів: ' + str(subscribed) + '\nВідписаних юзерів: ' + str(unsubscribed), chat)
        elif action == 'viewlimit':
            curs.execute("SELECT news_limit FROM users WHERE telegram_id='{}'".format(id))
            limit = curs.fetchone()[0]
            send_message('Твій ліміт у щоденній підбірці становить '+str(limit)+' новин. Щоб змінити, скористайся /limit', id)
        elif action == 'limit':
            if len(text[0]) == 0:
                curs.execute("UPDATE users SET command='limit' WHERE telegram_id='{}'".format(id))
                conn.commit()
                send_message('Надішли мені ліміт новин у вигляді одного цілого числа)) /cancel, щоб скасувати', id)
            else:
                print(text[0])

                try:
                    text=int(text[0])
                    print(True)
                    if text < 1000:
                        curs.execute("UPDATE users SET news_limit={} WHERE telegram_id='{}'".format(text, id))
                        send_message('Ліміт встановлено!', id)
                    else:
                        send_message('Число не підходить. Спробуй ще раз! /limit', id)
                except ValueError:
                    send_message('Число не підходить. Спробуй ще раз! /limit', id)
                curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                conn.commit()

        elif action == 'help':

            send_help_big(text, chat)
            send_inline_keyboard([['Обрати цікаві теми', '/themes'], ['Відібрати новинні веб-сайти', '/websites'],
                                      ['Вказати час отримання новин', '/setnewstime'], ['Переглянути свої ключові слова', '/keywords'], ['Отримати останні новини', '/getlastnews']], chat, 'Швидкі команди:')
        elif action == 'nomatch':
            send_inline_keyboard([['Обрати цікаві теми', '/themes'], ['Відібрати новинні веб-сайти', '/websites'],
                                      ['Вказати час отримання новин', '/setnewstime'], ['Переглянути свої ключові слова', '/keywords']], chat, 'Щось я тебе не розумію 😔😔😔 Можливо ти хотів:')
            #send_help_big(text, chat)
        else:
            send_message(text, id)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def send_help(text, chat_id):
    text = 'Тебе вітає NewsKit! \n Я - чат-бот, який надсилатиме тобі підбірку свіжих фільтрованих новин у зручний час з обраних новинних веб-сайтів.\n \n <code>Увага! Я поки знаходжусь в розробці і ти користуєшся MVP (найменшою робочою версією), тому поки я підтримую лише 1 новинний сайт. Чекай оновлення зовсім скоро! </code> \n \n Виявлені баги надсилай до <a href="https://www.facebook.com/dmytro.lopushanskyy">Дмитра Лопушанського</a> або <a href="https://www.facebook.com/mlastovski">Марка Ластовського</a>'

    send_message_html(text, chat_id)


def send_help_big(text, chat_id):
    text = ' Я - чат-бот, який надсилатиме тобі підбірку свіжих фільтрованих новин у зручний час з обраних новинних веб-сайтів.\n \n Щоб бути в курсі всіх подій, можеш підписатись на <a href="https://www.facebook.com/newskitbot">мою сторінку Facebook</a> \n \n <code>Я поки знаходжусь в розробці і ти користуєшся MVP (найменшою робочою версією). Чекай оновлення зовсім скоро! </code> \n \n Виявлені баги надсилай до <a href="#"></a><a href="https://www.facebook.com/dmytro.lopushanskyy">Дмитра Лопушанського</a> або <a href="https://www.facebook.com/mlastovski">Марка Ластовського</a> \n \n <b>Алгоритм роботи:</b> 1) Ти пишеш мені свої ключові слова або обираєш цікаву тематику 2) Як тільки з\'являється нова стаття на вказаних сайтах, яка підійде тобі за ключовими словами, то я одразу надішлю в цей чат посилання на неї!  \n \n <i>Список команд боту:</i> \n \n<b>Початок</b> \n  /start \n \n <b>Додавання ключових слів</b> \n Додай слово1, слово2, слово3 \n \n <b>Видалення ключових слів</b> \n Вилучи слово1, слово2, слово3 \n \n <b>Припинити надсилання новин</b> \n стоп \n \n <b>Відновити надсилання новин</b> \n відновити \n \n  <b>Видалити свій аккаунт в бота</b> \n Видалити аккаунт' + \
           '\n \n <b>Допомога</b> \n Допомога'

    send_message_html(text, chat_id)


def send_message_html(text, chat_id):
    TelegramBot.sendMessage(chat_id, text, parse_mode='HTML')


def send_inline_keyboard(markup, chat_id, text):
    # markup example: [['text', 'callback_data'], ['text', 'callback_data', 'continue'], ['text', 'callback_data']]

    inline_keyboard = get_reply_markup(markup)

    if text:
        try:
            TelegramBot.sendMessage(chat_id, text, reply_markup=inline_keyboard)
        except telepot.exception.BotWasBlockedError:
            print('trying to remove user '+ str(chat_id))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Користувач '+ str(chat_id)+' видалив NewsKit, намагаюсь його видалити'))
            curs.execute("SELECT * FROM users WHERE telegram_id='{}'".format(chat_id))
            user = curs.fetchone()
            print(user)
            curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(chat_id))
            websites = ''
            for i in curs.fetchall():
                websites = websites + str(i[0]) + ', '

            curs.execute("INSERT INTO dead_users (telegram_id, first_name, last_name, username, block_date_stamp, block_date_usual, using_days, websites, parse_mode, keywords, themes, language) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(user[1], user[2], user[9], user[10], datetime.now().timestamp(), datetime.now(), (datetime.now().timestamp() - float(user[8]))/86400, websites, user[7], user[3], user[6], user[11]))
            conn.commit()
            curs.execute("DELETE FROM users WHERE telegram_id='{}'".format(chat_id))
            curs.execute("DELETE FROM user2website WHERE user_id='{}'".format(chat_id))
            conn.commit()
            print('bot blocked!' + str(chat_id))
            curs.execute("SELECT id FROM users")
            users_quan = len(curs.fetchall())
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Користувач ' + user[2] + ' (' + str(user[1]) + ') видалив NewsKit. Загальна кількість активних юзерів: ' + str(users_quan) + str(user)))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Користувач ' + user[2] + ' (' + str(user[1]) + ') видалив NewsKit. Загальна кількість активних юзерів: ' + str(users_quan)))

            chat_info = TelegramBot.getChat(chat_id)
            try:
                last_name = chat_info['last_name']
            except:
                last_name = ''

            try:
                username = chat_info['username']
            except:
                username = ''

            if not last_name:
                last_name = ''

            curs.execute("UPDATE users SET last_name='{}', username='{}' WHERE telegram_id='{}'".format(last_name, username, chat_id))
            conn.commit()

            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'надіслано з сенд кіборд'))
    else:
        return None

def get_reply_markup(markup, type=None, forward=None):
    inline_keyboard = []

    for phrase in markup:
        current = InlineKeyboardButton(text=phrase[0], callback_data=phrase[1])
        if len(phrase) == 2:
            inline_keyboard.append([current])
        else:
            inline_keyboard[-1].append(current)
    print('forward', forward)
    if type == 'theme' and forward:
        inline_keyboard.append([InlineKeyboardButton(text='Далі ➡️', callback_data='/news_language newskit')])
    elif type == '_news_language' and forward:
        inline_keyboard.append([InlineKeyboardButton(text='Далі ➡️', callback_data='/websites newskit')])
    elif type == 'website' and forward:
        inline_keyboard.append([InlineKeyboardButton(text='Далі ➡️', callback_data='/setnewstime newskit')])
    elif type == 'time' and forward:
        inline_keyboard.append([InlineKeyboardButton(text='Далі ➡️', callback_data='/endtour')])

    print('inline_keyboard', inline_keyboard)
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return keyboard


def send_choose(list, chosen_list, text, type, forward=None):
    #filtring from empties
    if ' ' in chosen_list:
        chosen_list.remove(' ')
    elif '' in chosen_list:
        chosen_list.remove('')

    if text[0] in chosen_list:
        chosen_list.remove(text[0])
    else:
        chosen_list.append(text[0])
    print(chosen_list, forward)
    markup = []
    i = 1
    for list_item in list:
        list_item_filtered = ''.join(replace(list_item,[("'", '')]))
        if list_item_filtered in chosen_list:
            word_new = '✅️' + list_item
        else:
            word_new = list_item
        if i%2==1:
            if forward:
                markup.append([word_new, '/chosen' + type + ' ' + list_item + ' і forward'])
            else:
                markup.append([word_new, '/chosen' + type + ' ' + list_item])
        else:
            if forward:
                markup.append([word_new, '/chosen' + type + ' ' + list_item + ' і forward', 'continue'])
            else:
                markup.append([word_new, '/chosen' + type + ' ' + list_item, 'continue'])
        i+=1

    if type == 'theme' and forward:
        markup.append(['Далі ➡️', '/news_language newskit'])
    elif type == 'website' and forward:
        markup.append(['Далі ➡️', '/setnewstime newskit'])
    elif type == '_news_language' and forward:
        markup.append(['Далі ➡️', '/websites newskit'])

    print(markup)
    return markup

def send_btn_keyboard(chat_id):
    pass
    # TelegramBot.sendMessage(chat_id, 'testing custom keyboard',
    #                         reply_markup=ReplyKeyboardMarkup(
    #                             keyboard=[
    #                                 [KeyboardButton(text="Yes"), KeyboardButton(text="No")]
    #                             ]
    #                         ))

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        # if len(updates["result"]) > 0:
        #     last_update_id = get_last_update_id(updates) + 1
        #     echo_all(updates)
        try:
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                try:
                    echo_all(updates)
                except TypeError:
                    print('Error')
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'ERROR!!! + TypeError'))
        except Exception as e:
            print('Error_' + str(e))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'ERROR!!! ' + str(e)))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'ERROR!!! ' + str(e)))
        time.sleep(0.5)


if __name__ == '__main__':
    main()
