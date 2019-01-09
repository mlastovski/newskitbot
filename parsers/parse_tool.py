import re

# importing stopwords and converting them to the list


def extract_keywords(article_text, language, limit=4):
    if language == 'en':
        file_name = 'stopwords.txt'
    elif language == 'de':
        file_name = 'stopwords_de.txt'
    elif language == 'ru':
        file_name = 'stopwords_ru.txt'
    else:
        file_name = 'stopwords_ua.txt'

    with open(file_name, 'r') as myfile:
        stopwords = myfile.read().replace('\n', ' ')
        stopwords = re.sub('\W+',' ', stopwords )
        stopwords = stopwords.split(' ')

    for word in stopwords:
        while word in article_text: article_text.remove(word)
    final_words = [item for item in article_text if not item.isdigit()]
    filter(lambda a: a != ' ', final_words)
    while '' in final_words:
        final_words.remove('')

    final_words = {i:final_words.count(i) for i in final_words}
    search_num = limit #minimum number of times that the word should appear in the article
    final_text = []
    for word, num in final_words.items():
        if num >= search_num:
            final_text.append(word)
    #print(final_text, title_text, link)

    final_text = ' '.join(final_text)

    return final_text

# removing symbols for better understanding words
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
    list = [s.replace(".", '') for s in list]
    list = [s.replace("@", '') for s in list]
    list = [s.replace("#", '') for s in list]
    list = [s.replace("$", '') for s in list]
    list = [s.replace("%", '') for s in list]
    list = [s.replace("&", '') for s in list]
    list = [s.lower() for s in list]
    return list

