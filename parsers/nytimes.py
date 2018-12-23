# coding: utf8
from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
from parsers.parse_tool import extract_keywords, remove_bad_characters



def nytimes():
    data = requests.get("https://www.nytimes.com/section/world", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find('section', {'class': 'tab-panel'}).find('div', {'class': 'stream'}).find('ol', {'class': 'story-menu'}).find_all('li'):
        try:
            title_text = title.find('article').find('div', {'class': 'story-body'}).find('a', {'class': 'story-link'}).find('div', {'class': 'story-meta'}).find('h2').get_text()
            title_text = re.sub('\n', '', title_text)
            title_text = re.sub('  ', '', title_text)
            # print(title_text)
            link = title.find('article').find('div', {'class': 'story-body'}).find('a', {'class': 'story-link'}).get('href')
            # print(link)

            # Parsing each article
            try:
                structure = requests.get(link, headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                print('Pass through error!')
            eachpagesoup = BeautifulSoup(structure, "lxml")

            whole_article_text = []
            for eachpage in eachpagesoup.find_all('p'):
                article_text = eachpage.get_text()
                article_text = re.sub('\n', '', article_text)
                article_text = re.sub('\t', '', article_text)
                article_text = re.sub('\xe4', '', article_text)
                article_text = re.sub('\u201d', '', article_text)
                article_text = remove_bad_characters(article_text.split(' '))
                whole_article_text += article_text
                #print('article_text',article_text)

            final_text = extract_keywords(whole_article_text, 'en')
            # print(final_text)
            
            author = ' '
            date = datetime.now().timestamp()

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

        except AttributeError:
            print('AttributeError')

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating
    if len(articles) < 10:
        try:
            from bot import TOKEN
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Проблема з парсингом NY Times'))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN, 'Проблема з парсингом NY Times'))
        except ImportError:
            print("Import error (token), can't send message to bot")

    print(articles)
    
    return articles
if __name__ == '__main__':
    nytimes()
