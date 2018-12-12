# coding: utf8
from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
import collections

debug = False
test = True

def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )


def verge():
    # importing stopwords and converting them to the list
    with open('stopwords.txt', 'r') as myfile:
        stopwords = myfile.read().replace('\n', ' ')
        stopwords = re.sub('\W+', ' ', stopwords)
        stopwords = stopwords.split(' ')
        # print(stopwords)

    # getting data
    data = requests.get("https://www.theverge.com/", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)
    soup = BeautifulSoup(data, "lxml")
    articles = []

    for title in soup.find('div', {'class': 'l-main-content'}).find('div', {'class': 'l-col__main'}).find('div').find_all('div'):
        # print('1')
        try:
            # print('1')
            title_text = title.find('div', {'class': 'c-entry-box--compact'}).find('div', {'class': 'c-entry-box--compact__body'}).find('h2').find('a').get_text()
            # print(title_text)
            link = title.find('div', {'class': 'c-entry-box--compact'}).find('a').get('href')
            # print(link)
            try:
                structure = requests.get(link, headers={
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                print('Pass through error!')
            eachpagesoup = BeautifulSoup(structure, "lxml")

            for eachpage in eachpagesoup.find_all('p'):
                try:
                    article_text = eachpage.get_text()
                    article_text.encode('ascii', 'ignore')
                    # article_text = ''.join(e for e in article_text if e.isalnum())
                    article_text = re.sub('\W+', ' ', article_text)
                    article_text = article_text.lower()
                    article_text = article_text.split(' ')
                    article_text = [str(i) for i in article_text]
                    # print(article_text)
                except UnicodeEncodeError:
                    print("FIGNYA")

            # comparing stopwords and article_text
            filtered_words = list(set(stopwords) ^ set(article_text))
            counter = collections.Counter(filtered_words)
            # print(counter)
            if counter > 1:
                print('1')
                # print(filtered_words)
            else:
                print("Nema bilsche 1")
            # print(counter.most_common(20))
            # print(filtered_words)
            # filtered_words = list_duplicates(filtered_words)
            # print(list_duplicates(filtered_words))

            author = ''
            date = ''

            if title_text and link and author and date:
                article = {
                    'title': title_text,
                    'words': filtered_words,
                    'link': link,
                    'author': author,
                    'date': date
                }
                # print(article)
                articles.append(article)





        except AttributeError:
            try:
                from bot import TOKEN
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN,
                                                                                                           'Проблема з парсингом The Verge'))
            except ImportError:
                print("Import error (token), can't send message to bot")
                continue

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]]  # remove repeating
    return articles

if __name__ == '__main__':
    verge()
