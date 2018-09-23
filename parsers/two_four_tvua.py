from bs4 import BeautifulSoup
import requests
import lxml
#import scrapy
from datetime import datetime
import re
from apscheduler.schedulers.blocking import BlockingScheduler





def parse_24tvua():
    data = requests.get("https://24tv.ua/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []
    print('іщгз', soup)

    for title in soup.find("ul", {"class": "news-list"}).find_all('li'):
        title_text = title.find('a').find("div", {"class": "news-title"}).get_text()
        title_text = re.sub('\n', '', title_text)
        link = 'https://24tv.ua/' + title.find('a').get('href')
        author = ' '
        #date = title.find('a').find("div", {"class": "time"}).get_text().split(':')
        date = datetime.now().timestamp()

        #print('here',title_text, link, date, author)

        if title_text and link and author and date:
            article = {
                'title': title_text,
                'link': link,
                'author': author,
                'date': date
            }
            print(article)
            articles.append(article)

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles

if __name__ =='__main__':
    parse_24tvua()


