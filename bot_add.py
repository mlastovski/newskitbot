


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

def convert_time(list, timezone):
    new_list=[]
    for time in list:
        try:
            #print('Starting to convert time: '+ time)
            #print('Timezone:  ' + timezone)
            result = convert_time_from_gmt_to_local(time, timezone)
            #print('Result time:  ' + result)
            new_list.append(result)
        except:
            continue

    return new_list

def convert_back_time(list, timezone):
    new_list=[]
    print(list, timezone)
    for time in list:
        print(time)
        try:
            timezone_list = list(timezone)
            print(timezone_list)
            if timezone_list[0] == '+':
                timezone_list[0] = '-'
            elif timezone_list[0] == '-':
                timezone_list[0] = '+'

            timezone = ''.join(timezone_list)
            print(timezone)
            result = convert_time_from_gmt_to_local(time, timezone)
            print(result)
            new_list.append(result)
        except:
            continue

    return new_list

def convert_time_from_gmt_to_local(time_gmt, timezone):
    # time_gmt example: 12:24
    # timezone example: -13:48
    gmt_hour = int(time_gmt[:2])
    gmt_min = int(time_gmt[-2:])
    timezone_hour = int(timezone[:3])
    timezone_min = int(timezone[-2:])
    #print(gmt_hour, gmt_min, timezone_hour, timezone_min)
    if timezone_hour < 0:
        if abs(timezone_hour) <= gmt_hour:
            hour_result = gmt_hour - abs(timezone_hour)
        else:
            hour_result = abs(timezone_hour) - gmt_hour
            hour_result = 24 - hour_result
        if timezone_min <= gmt_min:
            min_result = gmt_min - timezone_min
        else:
            min_result = timezone_min - gmt_min
            min_result = 60 - min_result
            hour_result -= 1
    else:
        hour_result = abs(timezone_hour) + gmt_hour
        if hour_result > 24:
            hour_result = hour_result - 24

        min_result = abs(timezone_min) + gmt_min
        if min_result > 60:
            min_result = min_result - 60
            hour_result += 1

    if hour_result < 10:
        hour_result = '0' + str(hour_result)
    if min_result < 10:
        min_result = '0' + str(min_result)

    #print(str(hour_result) + ':' + str(min_result))

    return str(hour_result) + ':' + str(min_result)


if __name__ == '__main__':
    pass
    #convert_time_from_gmt_to_local()
