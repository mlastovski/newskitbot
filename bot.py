# encoding: UTF-8
import json
import requests
import time
from datetime import datetime
import urllib
import psycopg2
import os
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from bot_add import add_keywords, delete_keywords, convert_time, convert_back_time, convert_time_from_gmt_to_local
from parse import send
from timesend import addnewsheduler
from timezonefinder import TimezoneFinder
import pytz

os.environ['DATABASE_URL'] = 'postgres://cgvkxvyosmvmzd:f281ebb6771eaebb9c998d34665c60d917542d6df0ece9fa483da65d62b600e7@ec2-79-125-12-48.eu-west-1.compute.amazonaws.com:5432/dbrvpbkmj63vl8'
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

curs = conn.cursor()
curs.execute("SELECT value FROM static WHERE id=1")
TOKEN = curs.fetchone()[0]

curs.execute("SELECT value FROM static WHERE id=2")
TOKEN2 = curs.fetchone()[0]

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
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Користувач ' + user[2] + ' (' + str(user[1]) + ') видалив NewsKit. Загальна кількість активних юзерів: ' + str(users_quan) + str(user)))

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
                #print('passed loop: ', line, expression)
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
                    text = replace(text, [(',', ' і '), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                                          ("{", ''), ("}", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''),
                                          ("(", ''), (")", ''), ("*", ''), ("з моїх ключових слів", ''),
                                          ("до моїх ключових слів", ''), ("до списку новин", ''), ("в мою базу даних", ''),
                                          ("мені", ''), ("пліз слова", ''), ("пліз слово", ''), ("пліз", ''),
                                          ("ключові слова", '')])
                    text = text.split()
                    print('text before', text)
                    if text != ['скасувати']:
                        del text[:len(expression.split(' '))]
                    text = ' '.join(text)
                    text = replace(text, [(' і ', ';'), (' й ', ';'), (' та ', ';'), (';;', ';')])
                    text = text.split(';')
                    text = replace(text,
                                   [(',', ''), (";", ''), ('!', ''), ("'", ''), ("[", ''), ("]", ''),
                                    ("{", ''), ("}", ''), ("_", ''), ("=", ''), ("+", ''), ("|", ''), ("(", ''),
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
        #print('replace', str_from, str_to)
        if isinstance(var, str):
            var = var.replace(str_from, str_to)
        elif isinstance(var, list):
            list_new = []
            for word in var:
                word = word.replace(str_from, str_to)
                list_new.append(word)
            var = list_new
        #print('var', var)

    return var


def echo_all(updates):
    print(updates)
    for update in updates["result"]:
        print(update)
        try:
            try: #if its group
                try:
                    text = update['data']
                    mess_type = update["message"]["chat"]["type"]
                    print(mess_type)
                    chat = update["message"]["chat"]["id"]
                    id = update["message"]['chat']['id']
                    name = update["message"]['chat']['title']
                    last_name = 'group'
                    username = ''

                    mess_id=None
                except KeyError:
                    try:
                        text = update['callback_query']['data']
                        mess_type = update['callback_query']["message"]["chat"]["type"]
                        print(mess_type)
                        chat = update['callback_query']["message"]["chat"]["id"]
                        id = update['callback_query']["message"]['chat']['id']
                        name = update['callback_query']["message"]['chat']['title']
                        last_name = 'group'
                        username = ''

                        mess_id=update['callback_query']["message"]['message_id']
                    except KeyError:
                        text = update["message"]["text"]
                        mess_type = update["message"]["chat"]["type"]
                        print(mess_type)
                        chat = update["message"]["chat"]["id"]
                        id = update["message"]['chat']['id']
                        name = update["message"]['chat']['title']
                        last_name = 'group'
                        username = ''

                        mess_id=None

            except: #if its not
                print('here3')
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
                try:
                    text = update["message"]["text"]
                except:
                    location = update["message"]["location"]
                    latitude=location['latitude']
                    longitude=location['longitude']
                    text='/changetimezone'
                    print(location)
                mess_id=update["message"]['message_id']
        except KeyError:
            try:
                print('here4')
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

        curs.execute("SELECT * FROM users WHERE telegram_id ='{}'".format(id))
        user = curs.fetchone()
        if user == None:
            action = 'start'
        print(id)
        if id == 87676959:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Наташа Шелягина написала: ' + str(text)))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Наташа Шелягина написала: ' + str(text)))

        try:
            if action == 'start':
                # text = str([update['message']['chat']['id'], update['message']['chat']['first_name']])
                curs = conn.cursor()
                curs.execute("SELECT * FROM users WHERE telegram_id ='{}'".format(id))
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

                    if RepresentsInt(text[0]):
                        curs.execute("SELECT * FROM users WHERE telegram_id ='{}'".format(text[0]))
                        user = curs.fetchone()
                        invited = user[15]
                        if invited == '':
                            invited = str(id)
                        else:
                            invited = invited.split(', ')
                            if str(id) not in invited:
                                invited = ', '.join(invited) + ', ' + str(id)
                            else:
                                invited = ', '.join(invited)
                        curs.execute("UPDATE users SET invited='{}' WHERE telegram_id='{}'".format(invited, text[0]))
                        conn.commit()
                        requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Запрошено від користувача ' + text[0] + ' '+ user[2] + ' '+ user[9]))
                        requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Запрошено від користувача ' + text[0] + ' '+ user[2] + ' '+ user[9]))
                        print(user[15].split(', '), len(user[15].split(', ')))
                        requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, text[0], 'Користувач ' + name + ' '+ last_name + ' '+ ' доєднався до NewsKit за твоїм посиланням! Дякую за рекомендацію!'))
                        if len(invited.split(', ')) == 2:
                            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, text[0], 'Функція надсилання новин у повністю зручний ДЛЯ ТЕБЕ час відтепер доступна для тебе!\nСкористайся /newstime'))
                        elif len(invited.split(', ')) == 1:
                            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, text[0], 'Запроси ще 1 користувача, щоб розблокувати функцію надсилання новин у повністю зручний ДЛЯ ТЕБЕ час!'))
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
                curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}'".format(id))
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
                curs.execute("UPDATE users SET keywords ='{}' WHERE telegram_id ='{}'".format(
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
                curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}'".format(id))
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
                    "UPDATE users SET keywords ='{}' WHERE telegram_id ='{}'".format(str(present_words_list),
                                                                                                    id, name))
                conn.commit()
                send_message('Ваш список ключових слів: ' + str(present_words_list), chat)

            # elif action == 'deleteaccount':
            #     curs = conn.cursor()
            #     curs.execute("DELETE FROM users WHERE telegram_id ='{}'".format(id))
            #     conn.commit()
            #
            #     text = 'Ти більше не отримуватимеш щоденних розсилок(( Щоб відновити цю можливість напиши мені /start'
            #    send_message(text, chat)
            elif action == 'stop':
                curs = conn.cursor()
                curs.execute("SELECT status FROM users WHERE telegram_id ='{}'".format(id))
                status = int(curs.fetchone()[0])
                if status != 1:
                    curs.execute("UPDATE users SET status = 1 WHERE telegram_id ='{}'".format(id))
                    conn.commit()
                    text = 'Ти більше не отримуватимеш щоденних розсилок(( Щоб відновити цю можливість напиши мені /renew'
                else:
                    text = 'Ви вже відмовились від отримання новин раніше(( Щоб відновити цю можливість напиши мені /renew'

                send_message(text, chat)

            elif action == 'renew':
                curs = conn.cursor()
                curs.execute("SELECT status FROM users WHERE telegram_id ='{}'".format(id))
                status = int(curs.fetchone()[0])
                if status != 0:
                    curs.execute("UPDATE users SET status = 0 WHERE telegram_id ='{}'".format(id))
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
                curs.execute("SELECT theme FROM themes")
                all_themes = curs.fetchall()
                print('all_themes', all_themes)
                if text[0] == 'everything':
                    print(True)
                    theme_variable = all_themes
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Твої теми змінюються! Зачекай декілька секунд!')
                else:
                    theme_variable = [[text[0]]]

                try:
                    mode = text[1]
                except IndexError:
                    mode = None

                for var_theme in theme_variable:
                    text[0] = var_theme[0]


                    print('mode', mode, 'text0', text)
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
                    curs.execute("UPDATE users SET themes='{}' WHERE telegram_id = '{}'".format(', '.join(themes)+', ', id))
                    conn.commit()

                    print('hererer', text[0])

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

                if mode:
                    markup.append(['Натиснути на всі кнопки!', '/chosentheme' +  ' everything' + ' і forward'])
                else:
                    markup.append(['Натиснути на всі кнопки!️', '/chosentheme' + ' everything'])
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
                    curs.execute("SELECT name FROM websites WHERE id ='{}'".format(website[0]))
                    chosen_websites.append(curs.fetchone()[0])
                print(websites, chosen_websites)
                # now we have 2 vars: websites - list of all supported websites and chosen_websites - list of chosen websites
                if text[0] == 'newskit':
                    markup = send_choose(websites, chosen_websites, text, 'website', True)
                else:
                    markup = send_choose(websites, chosen_websites, text, 'website')

                send_inline_keyboard(markup, chat, 'Обери цікаві тобі веб-сайти! З них тобі будуть надсилатися персоналізовані новини 😉')
            elif action == 'chosenwebsite':
                curs.execute("SELECT news_language FROM users WHERE telegram_id ='{}'".format(id))
                chosen_languages= curs.fetchone()[0].split(', ')

                curs.execute("SELECT * FROM websites" )
                fetchall = curs.fetchall()
                all_web=[]
                print(fetchall)
                for website in fetchall:
                    if website[3] in chosen_languages:
                        all_web.append([website[2]])
                print('websites', all_web)
                if text[0] == 'everything':
                    print(True)
                    web_variable = all_web
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Твої веб-сайти змінюються! Зачекай 5 секунд!')
                else:
                    web_variable = [[text[0]]]

                for web in web_variable:
                    text[0] = web[0]

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
                        curs.execute("SELECT name FROM websites WHERE id ='{}'".format(website[0]))
                        chosen_websites.append(curs.fetchone()[0].lower())
                    print(websites, chosen_websites, text, text[0])

                    #filtring from empties
                    if ' ' in chosen_websites:
                        chosen_websites.remove(' ')
                    elif '' in chosen_websites:
                        chosen_websites.remove('')

                    if text[0].lower() in chosen_websites:
                        chosen_websites.remove(text[0].lower())
                        db_action = 'delete'
                    else:
                        chosen_websites.append(text[0].lower())
                        db_action = 'add'
                    print(chosen_websites)
                    markup = []
                    i = 1

                    print(text[0])
                    curs.execute("SELECT id FROM websites WHERE lower(name) ='{}'".format(text[0].lower()))
                    website_id = curs.fetchone()[0]
                    if db_action == 'delete':
                        curs.execute("DELETE FROM user2website WHERE website ='{}' and user_id ='{}'".format(website_id, id))
                        conn.commit()
                    else:
                        curs.execute("INSERT INTO user2website (website, user_id) VALUES ('{}', '{}')".format(website_id, id))
                        conn.commit()

                for website in websites:
                    website_filtered = ''.join(replace(list(website),[("'", '')]))
                    if website_filtered.lower() in chosen_websites:
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

                if mode:
                    markup.append(['Натиснути на всі кнопки!', '/chosenwebsite' +  ' everything' + ' і forward'])
                else:
                    markup.append(['Натиснути на всі кнопки!️', '/chosenwebsite' + ' everything'])

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


            elif action == 'setnewstime':

                if text[0] != '':
                    mode = text[0]
                    phrase = ' і forward'
                else:
                    mode = None
                    phrase = ''

                curs.execute("SELECT parse_mode FROM users WHERE telegram_id ='{}'".format(id))
                parse_mode = curs.fetchone()[0]

                curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                timezone = curs.fetchone()[0]

                now_time = str(datetime.now().time()).split(':')[0] +':'+ str(datetime.now().time()).split(':')[1]

                if ':' in parse_mode:
                    if ',' in parse_mode:
                        times = parse_mode.split(', ')
                    else:
                        times = [parse_mode]
                    markup = [['Одразу', '/chosentime immediate'], ['Щогодини', '/chosentime everyhour', 'continue']]
                    i = 0
                    print('times', times)
                    times = convert_time(times, timezone)
                    print(times)

                    for time in times:
                        i+=1
                        new = ['✅' + time, '/deletetime ' + time]
                        if i%3==0 or i%3==2:
                            new.append('continue')

                        markup.append(new)

                    markup.append(['Додати час отримання!', '/newstime'])
                    markup.append(['Змінити часовий пояс!', '/changetimezone newskit'])

                    print(markup)


                    send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
                else:
                    parse_possible = ['immediate', '09:00', 'everyhour', '12:00', '21:00']
                    parse_all = [['Одразу', '/chosentime immediate'], ['О 12 годині', '/chosentime 12:00', 'continue'] ,['Щогодини протягом дня', '/chosentime everyhour'],
                                              ['О 9 ранку', '/chosentime 09:00'], ['О 9 вечора', '/chosentime 21:00', 'continue']]
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
                    markup.append(['ВКАЗАТИ СВІЙ ЧАС!', '/newstime'])
                    markup.append(['Змінити часовий пояс!', '/changetimezone newskit'])
                    print(markup)

                    if text[0] == 'newskit':
                        markup.append(['Далі ➡️', '/endtour'])

                    send_inline_keyboard(markup, chat,'Коли ти хочеш отримувати новини?\nТочна година зараз у тебе: '+convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
            elif action == 'deletetime':
                text = text[0]
                print('deleting ', text)
                curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                timezone = curs.fetchone()[0]

                curs.execute("SELECT parse_mode FROM users WHERE telegram_id='{}'".format(id))
                previous_time = curs.fetchone()[0]

                print(previous_time)

                now_time = str(datetime.now().time()).split(':')[0] +':'+ str(datetime.now().time()).split(':')[1]

                if ':' in previous_time:
                    if ',' in previous_time:
                        times = previous_time.split(', ')
                    else:
                        times = [previous_time]

                print(times)
                times = convert_time(times, timezone)

                if text in times:
                    times.remove(text)


                print(times)
                i=0
                markup = [['Одразу', '/chosentime immediate'], ['Щогодини', '/chosentime everyhour', 'continue']]
                for time in times:
                    i+=1
                    new = ['✅' + time, '/deletetime ' + time]
                    if i%3==0 or i%3==2:
                        new.append('continue')

                    markup.append(new)
                markup.append(['Додати час отримання!', '/newstime'])
                markup.append(['Змінити часовий пояс!', '/changetimezone newskit'])

                print(markup)

                reply_markup = get_reply_markup(markup)

                print('times', times)

                if times == []:
                    print(True)
                    parse_mode = 'everyhour'
                    curs.execute("UPDATE users SET parse_mode = 'everyhour' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    markup = [['Одразу', '/chosentime immediate'], ['О 12 годині', '/chosentime 12:00', 'continue'], ['✅Щогодини протягом дня', '/chosentime everyhour'], ['О 9 ранку', '/chosentime 09:00'], ['О 9 вечора', '/chosentime 21:00', 'continue'], ['ВКАЗАТИ СВІЙ ЧАС!', '/newstime'], ['Змінити часовий пояс!', '/changetimezone newskit']]
                    reply_markup = get_reply_markup(markup)
                    if mess_id:
                        try:
                            TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Було видалено всі години надсилання новин, тому я тебе автоматично перевів на отримання новин щогодини! Можеш змінити цей час нижче:)', reply_markup=reply_markup)
                        except telepot.exception.TelegramError:
                            send_inline_keyboard(markup, chat, 'Було видалено всі години надсилання новин, тому я тебе автоматично перевів на отримання новин щогодини! Можеш змінити цей час нижче:)')
                    else:
                        send_inline_keyboard(markup, chat, 'Було видалено всі години надсилання новин, тому я тебе автоматично перевів на отримання новин щогодини! Можеш змінити цей час нижче:)')
                else:
                    print(True, False)
                    if mess_id:
                        try:
                            print('herere')
                            TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс', reply_markup=reply_markup)
                        except telepot.exception.TelegramError:
                            send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
                    else:
                        send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')

                    print('hee')
                    curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                    timezone = curs.fetchone()[0]

                    print('times)))', times, timezone)
                    timezone_list = list(timezone)
                    print(timezone_list)
                    if timezone_list[0] == '+':
                        timezone_list[0] = '-'
                    elif timezone_list[0] == '-':
                        timezone_list[0] = '+'

                    timezone = ''.join(timezone_list)
                    print(timezone)
                    times = convert_time(times, timezone)
                    times = ', '.join(times)
                    print('times', times)

                    curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id='{}'".format(times, id))
                    conn.commit()
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

                curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                timezone = curs.fetchone()[0]

                curs.execute("SELECT parse_mode FROM users WHERE telegram_id ='{}'".format(id))
                parse_mode = curs.fetchone()[0]

                if ':' in parse_mode and (text[0] == 'immediate' or text[0] == 'everyhour'):
                    print(text[0], parse_mode)
                    if ',' in parse_mode:
                        times = convert_time(parse_mode.split(', '), timezone)
                        times = ', '.join(times)
                    else:
                        times = convert_time([parse_mode], timezone)[0]
                    print('dsjk', times)

                    if times not in ['12:00', '21:00', '09:00']:
                        markup = [['Так, змінити', '/chosentime ' + text[0] + ' true' ], ['Ні, скасувати', '/chosentime false', 'continue']]
                        reply_markup = get_reply_markup(markup)
                        if mess_id:
                            try:
                                TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='При виборі "Одразу" або "Щогодини" ти більше не отримуватимеш новини о ' + times + '. Продовжити?', reply_markup=reply_markup)
                            except telepot.exception.TelegramError:
                                send_inline_keyboard(markup, chat, 'При виборі "Одразу" або "Щогодини" ти більше не отримуватимеш новини о ' + parse_mode + '. Продовжити?')
                        else:
                            send_inline_keyboard(markup, chat, 'При виборі "Одразу" або "Щогодини" ти більше не отримуватимеш новини о ' + parse_mode + '. Продовжити?')

                        return
                    else:
                        parse_mode = text[0]
                elif text[0] == 'false':
                    curs.execute("SELECT parse_mode FROM users WHERE telegram_id ='{}'".format(id))
                    parse_mode = curs.fetchone()[0]

                    curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                    timezone = curs.fetchone()[0]

                    now_time = str(datetime.now().time()).split(':')[0] +':'+ str(datetime.now().time()).split(':')[1]

                    if ':' in parse_mode:
                        if ',' in parse_mode:
                            times = parse_mode.split(', ')
                        else:
                            times = [parse_mode]
                        markup = [['Одразу', '/chosentime immediate'], ['Щогодини', '/chosentime everyhour', 'continue']]
                        i = 0
                        print('times', times)
                        times = convert_time(times, timezone)
                        print(times)

                        for time in times:
                            i+=1
                            new = ['✅' + time, '/deletetime ' + time]
                            if i%3==0 or i%3==2:
                                new.append('continue')

                            markup.append(new)

                        markup.append(['Додати час отримання!', '/newstime'])
                        markup.append(['Змінити часовий пояс!', '/changetimezone newskit'])

                        print(markup)

                        reply_markup = get_reply_markup(markup)
                        if mess_id:
                            try:
                                TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс', reply_markup=reply_markup)
                            except telepot.exception.TelegramError:
                                send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
                        else:
                            send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини? \nТочна година зараз у тебе: '+ convert_time_from_gmt_to_local(now_time, timezone)+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
                    return
                elif text[0] == 'immediate true' or text[0] == 'everyhour true':
                    parse_mode = text[0].split()[0]
                else:
                    parse_mode = text[0]

                if parse_mode in ['12:00', '21:00', '09:00']:
                    timezone_list = list(timezone)
                    print(timezone_list)
                    if timezone_list[0] == '+':
                        timezone_list[0] = '-'
                    elif timezone_list[0] == '-':
                        timezone_list[0] = '+'
                    timezone = ''.join(timezone_list)

                    times = convert_time([parse_mode], timezone)[0]
                    print(times)
                else:
                    times = parse_mode


                curs.execute("UPDATE users SET parse_mode = '{}' WHERE telegram_id ='{}'".format(times, id))
                conn.commit()

                now_time = str(datetime.now().time()).split(':')[0] +':'+ str(datetime.now().time()).split(':')[1]


                parse_possible = ['immediate', '09:00', 'everyhour', '12:00', '21:00']
                parse_all = [['Одразу', '/chosentime immediate'], ['О 12 годині', '/chosentime 12:00', 'continue'] ,['Щогодини протягом дня', '/chosentime everyhour'],
                                          ['О 9 ранку', '/chosentime 09:00'], ['0 9 вечора', '/chosentime 21:00', 'continue']]
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
                markup.append(['ВКАЗАТИ СВІЙ ЧАС!', '/newstime'])
                markup.append(['Змінити часовий пояс!', '/changetimezone newskit'])

                reply_markup = get_reply_markup(markup, 'time', mode)
                print('hereherehere')
                if mess_id:
                    try:
                        TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Коли ти хочеш отримувати новини?\nТочна година зараз у тебе: '+now_time+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс', reply_markup=reply_markup)
                    except telepot.exception.TelegramError:
                        send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини?\nТочна година зараз у тебе: '+now_time+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')
                else:
                    send_inline_keyboard(markup, chat, 'Коли ти хочеш отримувати новини?\nТочна година зараз у тебе: '+now_time+'. Якщо я помилився, то використай /changetimezone, щоб змінити часовий пояс')

            elif action == 'endtour':
                send_inline_keyboard([['Більше про мої можливості', '/help'], ['Отримати останні новини!', '/getlastnews']], chat, 'Вітаю! Ти налаштував свого найкращого новинного асистента! Я надсилатиму тобі новини за всіма критеріями, які ти мені вказав 😉✌️️')
            elif action == 'chooseall':
                if text[0] != '':
                    print('here', text[0])
                    curs.execute("SELECT id FROM websites WHERE lower(name) ='{}'".format(text[0]))
                    idiha = curs.fetchone()[0]
                    print(idiha)
                    curs.execute("SELECT keywords FROM user2website WHERE website ='{}' and user_id ='{}'".format(idiha, id))
                    try:
                        keywords = curs.fetchone()[0]
                    except TypeError:
                        return
                    print('keywords',keywords)
                    if keywords  == '':
                        curs.execute("UPDATE user2website SET keywords='*' WHERE website ='{}' and user_id ='{}'".format(idiha, id))
                    else:
                        curs.execute("UPDATE user2website SET keywords='' WHERE website ='{}' and user_id ='{}'".format(idiha, id))
                    conn.commit()

                    curs.execute("SELECT website FROM user2website WHERE keywords ='*' and user_id ='{}'".format(id))
                    websites = []
                    for i in curs.fetchall():
                        curs.execute("SELECT name FROM websites WHERE id ='{}'".format(i[0]))
                        websites.append(curs.fetchone()[0])
                    print(websites)

                    curs.execute("SELECT website FROM user2website WHERE user_id ='{}'".format(id))
                    user_web = []
                    for i in curs.fetchall():
                        curs.execute("SELECT name FROM websites WHERE id ='{}'".format(i[0]))
                        user_web.append(curs.fetchone()[0])
                    print(user_web)

                    markup=[]
                    i=1
                    for website in user_web:
                        if website in websites:
                            markup.append(['▶️' + website + '◀️', '/chooseall ' + website])
                        else:
                            markup.append([website, '/chooseall ' + website])

                        if i%2==0:
                            markup[-1].append('continue')
                        i+=1
                    print(id, mess_id, markup)
                    reply_markup = get_reply_markup(markup)
                    #TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️', reply_markup=reply_markup)

                    if mess_id:
                        try:
                            TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️', reply_markup=reply_markup)
                        except telepot.exception.TelegramError:
                            send_inline_keyboard(markup, chat, 'Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️')
                    else:
                        send_inline_keyboard(markup, chat, 'Якщо хочеш почати/перестати отримувати ВСІ свіжі статті з певного новинного веб-сайту, то обери його нижче️ ⬇️⬇️⬇️')
                    print('finished!')
                else:
                    print('here2', text[0])
                    curs.execute("SELECT website FROM user2website WHERE keywords ='*' and user_id ='{}'".format(id))
                    websites = []
                    for i in curs.fetchall():
                        curs.execute("SELECT name FROM websites WHERE id ='{}'".format(i[0]))
                        websites.append(curs.fetchone()[0])
                    print(websites)

                    curs.execute("SELECT website FROM user2website WHERE user_id ='{}'".format(id))
                    user_web = []
                    for i in curs.fetchall():
                        curs.execute("SELECT name FROM websites WHERE id ='{}'".format(i[0]))
                        user_web.append(curs.fetchone()[0])
                    print(user_web)

                    markup=[]
                    i=1
                    for website in user_web:
                        if website in websites:
                            markup.append(['▶️' + website + '◀️', '/chooseall ' + website])
                        else:
                            markup.append([website, '/chooseall ' + website])

                        if i%2==0:
                            markup[-1].append('continue')
                        i+=1

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
                curs.execute("SELECT invited FROM users WHERE telegram_id ='{}'".format(id))
                invited = curs.fetchone()[0]
                print(invited, len(invited.split(', ')))
                curs.execute("SELECT special_offer FROM users WHERE telegram_id='{}'".format(id))
                special_offer = curs.fetchone()[0]
                if special_offer == 'true':
                    logic = True
                else:
                    logic = False
                if invited == '' and not logic:
                    send_message('Для того, щоб використовувати суперкруту функцію надсилання новин у повністю зручний ДЛЯ ТЕБЕ час (з точністю до 1 хвилини!), потрібно запросити 2 друзів до NewsKit! \n\nТи вже запросив 0 друзів\n\nПоділися з друзями посиланням нижче: \n\nhttps://t.me/newskit_bot?start=' + str(id), id)
                elif len(invited.split(', ')) < 2 and not logic:
                    send_message('Для того, щоб використовувати суперкруту функцію надсилання новин у повністю зручний ДЛЯ ТЕБЕ час (з точністю до 1 хвилини!), потрібно запросити 2 друзів до NewsKit! \n\nТи вже запросив '+ str(len(invited.split(', '))) + ' друга\n\nПоділися з друзями посиланням нижче: \n\nhttps://t.me/newskit_bot?start=' + str(id), id)
                else:
                    if len(text[0]) == 0:
                        curs.execute("UPDATE users SET command='newstime' WHERE telegram_id='{}'".format(id))
                        conn.commit()
                        send_message('Надішли мені час, коли ти хочеш отримувати новини. Дотримуйся такого формату: \n10:47, 12:21, 20:19 \n/cancel, щоб скасувати', id)
                    else:
                        curs.execute("SELECT timezone FROM users WHERE telegram_id ='{}'".format(id))
                        timezone = curs.fetchone()[0]

                        print(text[0])
                        input = text[0]
                        if ', ' in input:
                            input = input.split(', ')
                        elif ',' in input:
                            input = input.split(',')
                        else:
                            input = [input]

                        count = 0
                        for text in input:
                            count += 1
                            try:
                                hours=int(text.split(':')[0])
                                minutes=int(text.split(':')[1])
                                print(hours, minutes)
                                if hours <= 24 and hours >= 0 and minutes < 60 and minutes >= 0 or hours == 24 and minutes == 0:
                                    timezone_list = list(timezone)
                                    print(timezone_list)
                                    if timezone_list[0] == '+':
                                        timezone_list[0] = '-'
                                    elif timezone_list[0] == '-':
                                        timezone_list[0] = '+'

                                    timezone_list = ''.join(timezone_list)
                                    print('tm changed ',timezone_list)
                                    result_time = convert_time([text], timezone_list)
                                    addnewsheduler(result_time, id)
                                    send_message('Час '+str(text)+' встановлено! Напиши /setnewstime, щоб контролювати твій час отримання новин!', id)
                                else:
                                    send_message('Час '+str(text)+' не підходить. Напиши час у форматі ГГ:ХХ. Наприклад, 09:21. Спробуй ще раз! /newstime', id)
                                curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                                conn.commit()
                            except:
                                send_message('Час '+str(text)+' не підходить. Напиши час у форматі ГГ:ХХ. Наприклад, 09:21. Спробуй ще раз! \nЩоб скасувати, натисни /cancel', id)
            elif action == 'invite':
                curs.execute("SELECT invited FROM users WHERE telegram_id ='{}'".format(id))
                invited = curs.fetchone()[0]
                print(invited, len(invited.split(', ')))
                friends=[]
                if invited != '':
                    quantity = str(len(invited.split(', ')))
                    for i in invited.split(', '):
                        curs.execute("SELECT * FROM users WHERE telegram_id ='{}'".format(i))
                        friend = curs.fetchone()
                        print(friend)
                        friends.append(friend[2] + ' ' + friend[9])
                else:
                    quantity = '0'

                friends = ', '.join(friends)
                print(friends)

                send_message('Ти вже запросив '+ quantity +' друзів: '+ friends +'\n\nЩоб запросити більше, поділися з друзями посиланням нижче: \n\nhttps://t.me/newskit_bot?start=' + str(id), id)

            elif action == 'feedback':
                print(text)
                if len(text[0]) == 0:
                    curs.execute("UPDATE users SET command='feedback' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    send_message('Надішли мені фідбек наступним повідомленням! \n/cancel, щоб скасувати', id)
                else:
                    if text[0] == 'offer':
                        curs.execute("UPDATE users SET command='feedback' WHERE telegram_id='{}'".format(id))
                        conn.commit()
                        send_message('Надішли мені твою пропозицію наступним повідомленням! /cancel, щоб скасувати', id)
                    else:
                        curs.execute("SELECT last_feedback_send FROM users WHERE telegram_id ='{}'".format(id))
                        try:
                            last_feedback_send = float(curs.fetchone()[0])
                        except:
                            last_feedback_send = 0
                        print(last_feedback_send)
                        if datetime.now().timestamp() - int(last_feedback_send) < 2:
                            return
                        elif datetime.now().timestamp() - int(last_feedback_send) < 5:
                            send_message('Фідбек не надіслано(( Спрацював захист від спаму! Спробуй через хвилину!', chat)
                            curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                        else:
                            curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                            send_message('Я надіслав твій фідбек!', chat)
                            curs.execute("UPDATE users SET last_feedback_send='{}' WHERE telegram_id='{}'".format(str(datetime.now().timestamp()), id))
                            conn.commit()
            elif action == 'feedbackonce':
                print(text)
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Фідбек! \n' + str(chat) + ' ' + str(name) + ' ' + last_name + '\n' + str(text[0])))
                try:
                    TelegramBot.editMessageText(msg_identifier=(id, mess_id), text='Дякую за відповідь! Вона дуже важлива для мене!')
                except telepot.exception.TelegramError:
                    send_message('Дякую за відповідь! Вона дуже важлива для мене!', chat)
            elif action == '/cancel':
                curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                conn.commit()
                send_message('Скасовано!', id)
            elif action == 'admin':
                if id == 138918380 or id == 373407132:
                    try:
                        curs.execute("SELECT command FROM users WHERE telegram_id='{}'".format(id))
                        command = curs.fetchone()[0]
                        print('comm', command, text)

                        if command:
                            admin_command = text[0]
                            print(admin_command)

                            if text[0].split()[1] == 'yes':
                                print('yes')
                                curs.execute("SELECT value FROM static WHERE id='4'")

                                text[0] = curs.fetchone()[0]
                                if not text[0]:
                                    return
                                send_status = True

                                command = '/admin'

                                curs.execute("UPDATE static SET value='' WHERE id='4'")
                                conn.commit()
                            elif text[0].split()[1] == 'no':
                                print('no')
                                send_message('Надсилання скасовано!', chat)

                                curs.execute("UPDATE static SET value='' WHERE id='4'")
                                conn.commit()
                                return
                            else:
                                send_status = False

                            text = text[0].split()
                            admin_action = text[0]
                            print('admin_action', admin_action, admin_command)

                            onemoretime=True

                            if text[0].startswith('touser') or text[0].startswith('keyboard'):
                                user_to_send_id = text[1]
                                del text[:2]
                                text = [user_to_send_id, ' '.join(text)]
                                print(text)

                            if admin_action == 'touser':
                                if send_status == False:
                                    curs.execute("SELECT * FROM users WHERE telegram_id = '{}'".format(text[0]))
                                    user = curs.fetchone()
                                    if user:
                                        send_message('Передогляд твого повідомлення до користувача ' + user[2] + ' ' + user[9] + ' (' + user[10] + '):', chat)
                                        get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, id, str(text[1])), text[0])
                                        send_inline_keyboard([['Так!', '/admin yes'], ['Ні!', '/admin no', 'continue']], chat, 'Надіслати?')
                                        curs.execute("UPDATE static SET value='{}' WHERE id='4'".format(admin_command))
                                        conn.commit()
                                    else:
                                        send_message('Користувача з айді ' + text[0] + ' не існує. Спробуй ще раз!', chat)
                                if send_status == True:
                                    get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, text[0], str(text[1])), text[0])
                                    send_message('Повідомлення успішно надіслано!', chat)

                            elif admin_action == 'keyboard':
                                try:
                                    buttons = text[1].split(' / ')
                                    touser_text = buttons[0] # header text for keyboard
                                    del buttons[:1]
                                    print(buttons)

                                    markup = []
                                    for single_button_info in buttons:
                                        single_button_info = single_button_info.split(', ')
                                        markup.append(single_button_info)

                                    if send_status == False:
                                        curs.execute("SELECT * FROM users WHERE telegram_id = '{}'".format(text[0]))
                                        user = curs.fetchone()
                                        if user:
                                            send_message('Передогляд твого повідомлення до користувача ' + user[2] + ' ' + user[9] + ' (' + user[10] + '):', chat)
                                            send_inline_keyboard(markup, id, touser_text)
                                            send_inline_keyboard([['Так!', '/admin yes'], ['Ні!', '/admin no', 'continue']], chat, 'Надіслати?')
                                            curs.execute("UPDATE static SET value='{}' WHERE id='4'".format(admin_command))
                                            conn.commit()
                                        else:
                                            send_message('Користувача з айді ' + text[0] + ' не існує. Спробуй ще раз!', chat)
                                    if send_status == True:
                                        send_inline_keyboard(markup, user_to_send_id, touser_text)
                                        send_message('Повідомлення успішно надіслано!', chat)
                                except:
                                    send_message('Помилка!\nДля надсилання клавіатури юзеру має бути такий синтаксис запиту:\nkeyboard 1234567 header text / btn1, callback1 / btn2, callback2, continue / btn3, callback3 / btn4, callback4, continue', chat)

                            elif admin_action == 'search':
                                try:
                                    category = admin_command.split(': ')[0].split()[1]
                                    value = admin_command.split(': ')[1]
                                except:
                                    send_message('Помилка!\nДля пошуку використовуй такий синтаксис:\nПошук юзера: search user: search_word_or_id\nПошук підписників сайту: search web: website_name\nПошук отримувачів новин у певній годині: search time: time_request', chat)

                                if category == 'user':
                                    if value.isnumeric():
                                        curs.execute("SELECT * FROM users WHERE id ='{0}'".format(value.lower()))
                                    else:
                                        curs.execute("SELECT * FROM users WHERE lower(name) = '{0}' or lower(last_name) = '{0}' or lower(username) = '{0}'".format(value.lower()))

                                    user = curs.fetchall()
                                    if user:
                                        print(user)
                                        if len(user) > 1:
                                            send_message(str(user), chat)
                                        else:
                                            user = user[0]
                                            curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(user[1]))
                                            websites = ''
                                            for i in curs.fetchall():
                                                curs.execute("SELECT name FROM websites WHERE id='{}'".format(i[0]))
                                                websites = websites + curs.fetchone()[0] + ', '

                                            send_message(str(user) + '\n\nWebsites: ' + websites, chat)
                                    else:
                                        send_message('Користувача не знайдено!', chat)
                                elif category == 'web':
                                    curs.execute("SELECT id FROM websites WHERE lower(name)='{}'".format(value.lower()))
                                    website = curs.fetchone()[0]
                                    print(website)
                                    if website:
                                        curs.execute("SELECT * FROM user2website WHERE website='{}'".format(website))
                                        all_users = curs.fetchall()
                                        print(all_users)
                                        users = ''
                                        for i in all_users:
                                            print(i[1])
                                            try:
                                                curs.execute("SELECT name, last_name, username FROM users WHERE telegram_id='{}'".format(i[1]))
                                                users+=str(curs.fetchone()) + ', '
                                            except:
                                                print('Error with ', i)
                                        print(users)

                                        send_message('Всі підписники сайту '+ text[1]+ '('+str(len(users))+') : '+users, id)
                                elif category == 'time':
                                    curs.execute("SELECT * FROM users")
                                    users = curs.fetchall()
                                    result = []
                                    print(value.lower())
                                    for i in users:
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
                                        else:
                                            time = [time_send]
                                        print(time)
                                        if value.lower() in time:
                                            result.append(str(i[2]) + ' ' + str(i[9]) + ' ' + str(i[10]) + '\n')

                                send_message('Всі отримувачі новин о '+ value.lower() + ' ('+str(len(result))+'):\n'+''.join(result), id)

                            elif admin_action == 'toallusers':
                                curs.execute("SELECT telegram_id FROM users")
                                users = curs.fetchall()
                                print(len(users))
                                print(text)
                                del text[:1]
                                send_text = ' '.join(text)
                                print('Send to all users: ',send_text)
                                if send_status == False:
                                    send_message('Передогляд твого повідомлення УСІМ користувачам:', chat)
                                    get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, id, send_text), id)
                                    send_inline_keyboard([['Так!', '/admin yes'], ['Ні!', '/admin no', 'continue']], chat, 'Надіслати?')
                                    curs.execute("UPDATE static SET value='{}' WHERE id='4'".format(admin_command))
                                    conn.commit()
                                if send_status == True:
                                    send_message('Масову розсилку розпочато!', chat)
                                    print(True)
                                    for i in users:
                                        print(i[0], send_text)
                                        get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, i[0], send_text), i[0])
                                    send_message('Повідомлення успішно розіслано всім користувачам!', chat)

                            elif admin_action == 'add':
                                text.pop(0)
                                request = ' '.join(text)
                                print(request)

                                curs.execute("SELECT value FROM static WHERE id = 5")
                                additional_info = curs.fetchone()[0]

                                curs.execute("SELECT id, name, last_name, username FROM users WHERE additional_received ='true'")
                                additional_received = curs.fetchall()

                                if request == 'track':
                                    send_message(str(len(additional_received))+ ' юзерів отримали це повідомлення:\n'+additional_info, chat)
                                    return_text = ''
                                    for i in additional_received:
                                        return_text += str(i) + '\n'
                                    send_message(return_text, chat)
                                    return

                                if additional_info:
                                    print(True)
                                    if send_status == False:
                                        send_message('Потрібно замінити це повідомлення:\n'+additional_info+'\nЙого побачило '+str(len(additional_received))+' людей. Натомість таке повідомлення прийде всім користувачам під час їхньої розсилки: ', chat)
                                        get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, id, request), id)
                                        send_inline_keyboard([['Так!', '/admin yes'], ['Ні!', '/admin no', 'continue']], chat, 'ОК?')
                                        curs.execute("UPDATE static SET value='{}' WHERE id='4'".format(admin_command))
                                        conn.commit()
                                    if send_status == True:
                                        curs.execute("UPDATE static SET value ='{}' WHERE id='5'".format(request))
                                        conn.commit()
                                        curs.execute("UPDATE users SET additional_received ='false'")
                                        conn.commit()
                                        send_message('Оновлено!', chat)
                                else:
                                    print(False)
                                    if send_status == False:
                                        send_message('Таке повідомлення прийде всім користувачам під час їхньої розсилки: ', chat)
                                        get_json_from_url('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, id, request), id)
                                        send_inline_keyboard([['Так!', '/admin yes'], ['Ні!', '/admin no', 'continue']], chat, 'ОК?')
                                        curs.execute("UPDATE static SET value='{}' WHERE id='4'".format(admin_command))
                                        conn.commit()
                                    if send_status == True:
                                        curs.execute("UPDATE static SET value ='{}' WHERE id='5'".format(request))
                                        conn.commit()
                                        curs.execute("UPDATE users SET additional_received ='false'")
                                        conn.commit()
                                        send_message('Оновлено!', chat)



                            elif admin_action == 'aboutuser':
                                curs.execute("SELECT * FROM users WHERE telegram_id = '{}'".format(text[1]))
                                user = curs.fetchone()
                                print(user)
                                curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(user[1]))
                                websites = ''
                                for i in curs.fetchall():
                                    curs.execute("SELECT name FROM websites WHERE id='{}'".format(i[0]))
                                    websites = websites + curs.fetchone()[0] + ', '

                                send_message(str(user) + '\n\nWebsites: ' + websites, chat)
                            elif admin_action == 'allusers':
                                print('here')
                                curs.execute("SELECT * FROM users WHERE".format())
                                users = curs.fetchall()
                                send_message('Надсилається в SpamBot-і ' + websites, chat)
                                for person in users:
                                    curs.execute("SELECT website FROM user2website WHERE user_id='{}'".format(person[1]))
                                    websites = ''
                                    for i in curs.fetchall():
                                        curs.execute("SELECT name FROM websites WHERE id='{}'".format(i[0]))
                                        websites = websites + curs.fetchone()[0] + ', '
                                    requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id={}&text={}'.format(chat, str(person) + '\n\nWebsites: ' + websites))
                                send_message('Запит виконано!' + websites, chat)
                            elif admin_action == 'statistic':
                                curs.execute("SELECT * FROM users")
                                users = curs.fetchall()
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

                                        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id={}&text={}'.format(chat, 'Користувачу '+ i[2] + ' ' + i[9] + ' ' + i[10] + ' (' + str(i[1]) +')' +' сьогодні не надіслано новини. Теми юзера: ' +str(i[6]) + '. Сайти: '+ websites + '. Час: '+ times))
                                        not_received += 1
                                    else:
                                        users_received_today += 1
                                    sum += int(i[24])
                                requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id={}&text={}'.format(chat,'Сьогодні було надіслано ' + str(sum) + ' статей\nНовини отримали '+ str(users_received_today) + ' користувачів\nНовини не отримали '+ str(not_received)+ ' користувачів'))
                            else:
                                send_message('Такої команди в адмін-панелі не існує(( Спробуй ще раз. Або /cancel щоб вийти', chat)
                                onemoretime=True

                            if not onemoretime:
                                curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                                conn.commit()
                        else:
                            curs.execute("UPDATE users SET command='admin' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                            send_message('Доступ дозволено! Що мені зробити? \n/cancel, щоб скасувати', id)
                    except Exception as e:
                        send_message('В адмін-панелі такої команди не інсує або у тебе поганий синтаксис запиту! Спробуй ще раз або /cancel щоб повернутися до бота', chat)
                        print('Error: ' + str(e))
                        return
                else:
                    send_message('Для цієї команди необхідно мати вищий пропуск! Ти його, на жаль, не маєш(( Проте не засмучуйся)) Напиши /getlastnews і я потішу тебе останніми новинами!', chat)
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
                        if text < 1000 and text > 0:
                            curs.execute("UPDATE users SET news_limit={} WHERE telegram_id='{}'".format(text, id))
                            send_message('Ліміт встановлено!', id)
                            curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                        else:
                            send_message('Число не підходить. Спробуй ще раз! /cancel, щоб скасувати', id)
                    except ValueError:
                        send_message('Число не підходить. Спробуй ще раз! /cancel, щоб скасувати', id)
            elif action == 'changetimezone':
                print(text)
                if text == ['скасувати']:
                    TelegramBot.sendMessage(id, 'Скасовано!', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    break
                try:
                    print(longitude, latitude)
                    tf = TimezoneFinder()
                    country = tf.timezone_at(lng=longitude, lat=latitude)
                    print(country)
                    utc = pytz.utc

                    def offset(target):
                        """
                        returns a location's time zone offset from UTC in minutes.
                        """
                        today = datetime.now()

                        from pytz import timezone
                        tz_target = timezone(tf.certain_timezone_at(lat=target['lat'], lng=target['lng']))
                        # ATTENTION: tz_target could be None! handle error case
                        print('tz_target',tz_target)
                        if tz_target:
                            today_target = tz_target.localize(today)
                            today_utc = utc.localize(today)
                            print('utktk',today_utc, today_target)
                            result_here = int((today_utc - today_target).total_seconds() / 3600)
                            print('result_here',result_here)
                            if result_here < 10 and result_here > -10:
                                if result_here >=0:
                                    result_here = '+0'+ str(result_here)
                                else:
                                    result_here = '-0' + str(abs(result_here))
                            result_here = result_here + ':00'
                            return result_here
                        else:
                            TelegramBot.sendMessage(id, 'Я, на жаль, не можу визначити твій часовий пояс:( Спробуй обрати цей варіант зміни твого часовго поясу:',
                                    reply_markup=ReplyKeyboardMarkup(
                                        keyboard=[
                                            [KeyboardButton(text="Надіслати мою поточну годину")], [KeyboardButton(text="Скасувати")]
                                        ],
                                        one_time_keyboard=True,
                                        resize_keyboard=True,
                                        selective=True
                                    ))
                            return

                    bergamo = dict({'lat':latitude, 'lng':longitude})
                    result = offset(bergamo)
                    print(mess_id)
                    TelegramBot.sendMessage(id, 'Твій часовий пояс успішно змінено!\nGMT '+ str(result + '\nПеревір командою /setnewstime час отримання новин і зміни його, якщо потрібно!'),
                                    reply_markup=ReplyKeyboardRemove(
                                        remove_keyboard=True
                                    ))
                    curs.execute("UPDATE users SET timezone='{}' WHERE telegram_id='{}'".format(result, id))
                    conn.commit()

                except Exception as e:
                    print(id, e)
                    if int(id)< 0:
                        send_message("Надсилання локації у груповому чаті, на жаль, неможливе! Цей розділ буде скоро допрацьовано!", id)
                    else:
                        TelegramBot.sendMessage(id, 'Щоб встановити новий часовий пояс, обери один з варіантів нижче\nУвага! Зміна часового поясу призведе до зміни часу, коли отримуєш новини!',
                                    reply_markup=ReplyKeyboardMarkup(
                                        keyboard=[
                                            [KeyboardButton(text="Надіслати моє місцезнаходження", request_location=True)], [KeyboardButton(text="Надіслати мою поточну годину")], [KeyboardButton(text="Скасувати")]
                                        ],
                                        one_time_keyboard=True,
                                        resize_keyboard=True,
                                        selective=True
                                    ))
            elif action == 'timezone':
                print(True)
                print(text)
                if len(text[0]) == 0:
                    curs.execute("UPDATE users SET command='timezone' WHERE telegram_id='{}'".format(id))
                    conn.commit()
                    TelegramBot.sendMessage(id, 'Надішли мені твою поточну годину у форматі ГГ:ХХ! Наприклад, 20:19 \n/cancel, щоб скасувати',
                                    reply_markup=ReplyKeyboardRemove(
                                        remove_keyboard=True
                                    ))
                else:
                    print(text[0])
                    input = text[0]

                    now_hours = int(str(datetime.now().time()).split(':')[0])
                    now_min = int(str(datetime.now().time()).split(':')[1])
                    print(str(now_hours), str(now_min))
                    try:
                        hours=int(input.split(':')[0])
                        minutes=int(input.split(':')[1])
                        print(hours, minutes)
                        if hours <= 24 and hours >= 0 and minutes < 60 and minutes >= 0:
                            hour_difference = hours - now_hours
                            min_difference = minutes - now_min
                            print(hour_difference, min_difference)
                            if min_difference < 5 and min_difference > -5:
                                min_difference = 0
                                if hour_difference > 12:
                                    hour_difference = (24 - hour_difference) * -1
                                if hour_difference < -12:
                                    hour_difference = 24 + hour_difference

                                if hour_difference < 10 and hour_difference > -10:
                                    if hour_difference >=0:
                                        hour_difference = '+0'+ str(hour_difference)
                                    else:
                                        hour_difference = '-0' + str(abs(hour_difference))
                                else:
                                    if hour_difference >=0:
                                        hour_difference = '+'+ str(hour_difference)
                                    else:
                                        hour_difference = '-' + str(abs(hour_difference))

                                result = str(hour_difference) + ':00'
                                print('result',result)
                            else:
                                # if min_difference < 0 and hour_difference < 0 or  min_difference > 0 and hour_difference > 0:
                                #     result = str(hour_difference) + ':' + str(abs(min_difference))
                                if min_difference > 0 and hour_difference < 0:
                                    hour_difference = hour_difference + 1
                                    min_difference = 60 - min_difference
                                    if hour_difference == 0:
                                        hour_difference = '-00'
                                        result_special = True
                                    else:
                                        result_special = False
                                elif min_difference < 0 and hour_difference > 0:
                                    hour_difference = hour_difference - 1
                                    min_difference = 60 + min_difference
                                    result_special = False
                                else:
                                    result_special = False

                                if not result_special:
                                    if hour_difference > 12:
                                        hour_difference = (24 - hour_difference - 1) * -1
                                        min_difference = 60 - min_difference
                                    if hour_difference < -12:
                                        hour_difference = 24 + hour_difference -1
                                        if min_difference < 0:
                                            min_difference = 60 + min_difference
                                        else:
                                            min_difference = 60 - min_difference
                                            #hour_difference += 1

                                    if hour_difference < 10 and hour_difference > -10:
                                        if hour_difference >=0:
                                            hour_difference = '+0'+ str(hour_difference)
                                        else:
                                            hour_difference = '-0' + str(abs(hour_difference))
                                    else:
                                        if hour_difference >=0:
                                            hour_difference = '+'+ str(hour_difference)
                                        else:
                                            hour_difference = '-' + str(abs(hour_difference))

                                if min_difference < 10 and min_difference > -10:
                                    min_difference = '0' + str(abs(min_difference))
                                else:
                                    min_difference = str(abs(min_difference))

                                result = str(hour_difference) + ':' + min_difference
                                print('result',result)
                            curs.execute("UPDATE users SET timezone='{}' WHERE telegram_id='{}'".format(result, id))
                            conn.commit()
                            curs.execute("UPDATE users SET country='' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                            TelegramBot.sendMessage(id, 'Твій часовий пояс успішно змінено!\nGMT '+ result + '\nПеревір командою /setnewstime час отримання новин і зміни його, якщо потрібно!',
                                    reply_markup=ReplyKeyboardRemove(
                                        remove_keyboard=True
                                    ))
                            curs.execute("UPDATE users SET command='' WHERE telegram_id='{}'".format(id))
                            conn.commit()
                        else:
                            TelegramBot.sendMessage(id, 'На жаль, я не можу зрозуміти такий формат запису:(\nНадішли мені твою поточну годину у форматі ГГ:ХХ! Наприклад, 20:19. Спробуй ще раз! \n/cancel, щоб скасувати',
                                    reply_markup=ReplyKeyboardRemove(
                                        remove_keyboard=True
                                    ))
                    except:
                        TelegramBot.sendMessage(id, 'На жаль, я не можу зрозуміти такий формат запису:(\nНадішли мені твою поточну годину у форматі ГГ:ХХ! Наприклад, 20:19. Спробуй ще раз! \n/cancel, щоб скасувати',
                                    reply_markup=ReplyKeyboardRemove(
                                        remove_keyboard=True
                                    ))
            elif action == 'help':

                send_help_big(text, chat)
                send_inline_keyboard([['Обрати цікаві теми', '/themes'], ['Відібрати новинні веб-сайти', '/websites'],
                                          ['Вказати час отримання новин', '/setnewstime'], ['Переглянути свої ключові слова', '/keywords'], ['Отримати останні новини', '/getlastnews']], chat, 'Швидкі команди:')
            elif action == 'nomatch':
                if str(text) == '2019':
                    curs.execute("SELECT special_offer FROM users WHERE telegram_id='{}'".format(id))
                    if curs.fetchone()[0] == '':
                        curs.execute("UPDATE users SET special_offer='true' WHERE telegram_id='{}'".format(id))
                        conn.commit()
                        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Користувач ' + name + ' ' + last_name + ' заповнив форму-відгук!'))
                        requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Користувач ' + name + ' ' + last_name + ' заповнив форму-відгук!'))
                        send_message('Вухууу! Дякуємо за відгук! Зі святом тебе! Клікай на цю команду: /newstime і насолоджуйся крутими підбірками новин у ще зручніший час!', id)
                    else:
                        send_message('Доступ до нашого новорічного подарунка тобі вже надано! Клікай на цю команду: /newstime і насолоджуйся крутими підбірками новин у ще зручніший час!', id)
                    return
                send_inline_keyboard([['Обрати цікаві теми', '/themes'], ['Відібрати новинні веб-сайти', '/websites'],
                                          ['Вказати час отримання новин', '/setnewstime'], ['Переглянути свої ключові слова', '/keywords']], chat, 'Я тебе не зрозумів 😔 Можливо, тобі потрібно:')
                #send_help_big(text, chat)
                requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Unexpected request from ' + name + ' ' + last_name + ': ' + text))
                requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Unexpected request from ' + name + ' ' + last_name + ': ' + text))
            else:
                send_message(text, id)
        except:
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=138918380&text={}'.format('Помилка у користувача ' + name + ' ' + last_name + ': ' + text))
            requests.get('https://api.telegram.org/bot613708092:AAEYN4KQHf_MinZAtAqQqkREdBNvYPk8yYM/sendMessage?chat_id=373407132&text={}'.format('Помилка у користувача ' + name + ' ' + last_name + ': ' + text))



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

    if forward and type != '_news_language' :
        markup.append(['Натиснути на всі кнопки!', '/chosen' + type +  ' everything' + ' і forward'])
    elif type != '_news_language':
        markup.append(['Натиснути на всі кнопки!️', '/chosen' + type + ' everything'])

    if type == 'theme' and forward:
        markup.append(['Далі ➡️', '/news_language newskit'])
    elif type == 'website' and forward:
        markup.append(['Далі ➡️', '/setnewstime newskit'])
    elif type == '_news_language' and forward:
        markup.append(['Далі ➡️', '/websites newskit'])

    print(markup)
    return markup

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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
                    requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'ERROR)! + TypeError'))
        except Exception as e:
            print('Error: ' + str(e))
            curs.execute("Rollback")
            conn.commit()
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'ERROR))! ' + str(e)))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'ERROR))! ' + str(e)))
        #time.sleep(0.5)


if __name__ == '__main__':
    main()
