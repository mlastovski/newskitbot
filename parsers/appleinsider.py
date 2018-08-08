from bs4 import BeautifulSoup
import requests
import lxml
#import scrapy
from datetime import datetime
import re
from apscheduler.schedulers.blocking import BlockingScheduler


def appleinsider():
    data = requests.get("https://appleinsider.ru/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []


    for title in soup.find("main", {"class": "site-main"}).find_all('article'):
        title_text = title.find('header').find('h2').find('a').get_text()
        title_text = re.sub('\n', '', title_text)
        link = title.find('header').find('h2').find('a').get('href')
        author = ' '
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
    appleinsider()


