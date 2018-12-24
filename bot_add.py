


def add_keywords(conn, id, name, text, chat):
    from bot import replace, send_message

    curs = conn.cursor()
    curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}'".format(id, name))
    try:
        print('user', id, name)
        present_words = curs.fetchone()[0]
    except TypeError:
        present_words = ''
    present_words_list = present_words.split(', ')

    print('text',text)
    # text consists of received list of new keywords

    # loop for detecting repeating keywords
    isgoingtoberemoved = []
    for word in text:
        if word in present_words_list:
            isgoingtoberemoved.append(word)

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
        str(present_words_list + text), id))
    conn.commit()
    print('done', present_words_list + text)

def delete_keywords(conn, id, name, text, chat):
    from bot import replace, send_message
    print('text', text)
    curs = conn.cursor()
    curs.execute("SELECT keywords FROM users WHERE telegram_id ='{}'".format(id))
    present_words = curs.fetchone()[0]
    present_words_list = present_words.split(', ')

    # loop for removing chosen elements
    for should_remove in text:
        if should_remove in present_words_list:
            present_words_list.remove(should_remove)

    if len(present_words_list) == 1 and present_words_list[0] == '':
        present_words_list = ''.join(present_words_list)
    else:
        present_words_list = ', '.join(present_words_list)

    curs.execute(
        "UPDATE users SET keywords ='{}' WHERE telegram_id ='{}'".format(str(present_words_list),
                                                                                        id))
    conn.commit()
    print('done', present_words_list)

def convert_time(list):
    new_list=[]
    for time in list:
        try:
            hour = int(time[:2])
            if int(hour) < 23:
                hour = int(hour) + 2
            elif int(hour) == 23:
                hour = 1
            elif int(hour) == 24:
                hour = 2

            if int(hour) < 10:
                hour = '0' + str(hour)

            new_list.append(str(hour) + time[2:])
        except:
            continue

    return new_list

def convert_back_time(list):
    new_list=[]
    for time in list:
        try:
            hour = int(time[:2])
            if int(hour) > 2:
                hour = int(hour) - 2
            elif int(hour) == 2:
                hour = 24
            elif int(hour) == 1:
                hour = 23

            if int(hour) < 10:
                hour = '0' + str(hour)

            new_list.append(str(hour) + time[2:])
        except:
            continue

    return new_list

