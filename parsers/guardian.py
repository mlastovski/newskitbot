# coding: utf8
from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
import collections
from parsers.parse_tool import extract_keywords

debug = False
test = True

def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )

def guardian():
    # print('1')
    # importing stopwords and converting them to the list
    with open('stopwords.txt', 'r') as myfile:
        stopwords = myfile.read().replace('\n', ' ')
        stopwords = re.sub('\W+', ' ', stopwords)
        stopwords = stopwords.split(' ')
        # print(stopwords)

    # getting data
    data = requests.get("https://www.theguardian.com/international", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)
    soup = BeautifulSoup(data, "lxml")
    articles = []

    for title in soup.find('ul', {'class': 'headline-list'}).find_all('li'):
        try:
            # print('1')
            title_text = title.find('div').find('div').find('h3').find('a').find('span').find('span').get_text()
            # print(title_text)
            link = title.find('div').find('div').find('h3').find('a').get('href')
            # print(link)

            try:
                structure = requests.get(link, headers={
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                print('Pass through error!')
            eachpagesoup = BeautifulSoup(structure, "lxml")

            whole_article_text = []

            for eachpage in eachpagesoup.find_all('p'):
                try:
                    article_text = eachpage.get_text()
                    article_text.encode('ascii', 'ignore')
                    # article_text = ''.join(e for e in article_text if e.isalnum())
                    article_text = re.sub('\W+', ' ', article_text)
                    article_text = article_text.lower()
                    article_text = article_text.split(' ')
                    article_text = [str(i) for i in article_text]
                    whole_article_text+=article_text
                    # print(article_text)
                except UnicodeEncodeError:
                    print("FIGNYA")

            final_text = extract_keywords(whole_article_text, 'en')
            #print(final_text)

            author = ''
            date = ''

            if title_text and link:
                article = {
                    'title': title_text,
                    'words': final_text,
                    'link': link,
                    'author': author,
                    'date': date
                }
                print(article)
                articles.append(article)

            if len(articles) > 5:
                break

        except AttributeError:
            print('AttributeError')

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]]  # remove repeating
    print(len(articles), articles)

    if len(articles) < 6:
        try:
            from bot import TOKEN2
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN2, 'Проблема з парсингом Guardian'))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN2, 'Проблема з парсингом Guardian'))
        except ImportError:
            print("Import error (token), can't send message to bot")

    return articles

if __name__ == '__main__':
    guardian()
