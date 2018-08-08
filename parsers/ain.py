from bs4 import BeautifulSoup
import requests
import lxml
# import scrapy
from datetime import datetime
import re
from apscheduler.schedulers.blocking import BlockingScheduler

mon = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12'
}


def parse_ainua():
    data = requests.get("https://ain.ua/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for part in soup.find_all("div", {"class": "posts-list"}):
        for title in part.find_all("div", {"class": "post-item"}):
            try:
                title_text = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find(
                    "div", {"class": "left-column-top"}).find("h3", {"class": "post-title"}).get_text()
            except AttributeError:
                # print(title)
                continue
            title_text = re.sub('\n', '', title_text)
            link = title.find("a", {"class": "post-link"}).get('href')
            author = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find("div", {
                "class": "left-column-bottom"}).find("div", {"class": "author"}).find('a').get_text().replace('  ',
                                                                                                              '').replace(
                '\n', '')
            date = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find("div", {
                "class": "left-column-top"}).find("div", {"class": "category-wrapper"}).find('time').get_text()
            month = date.split(' ')[1].replace(',', '')
            # print(datetime.now().replace(hour=int(date.split(' ')[2].split(':')[0]), day=int(date.split(' ')[0]), minute=int(date.split(' ')[2].split(':')[1]), month=int(mon.get(month))))

            date = datetime.now().timestamp()
            # print('here',title_text, link, date, author)

            if title_text and link and author and date:
                article = {
                    'title': title_text,
                    'link': link,
                    'author': author,
                    'date': date
                }
                print(article)
                articles.append(article)

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]]  # remove repeating

    return articles


if __name__ == '__main__':
    parse_ainua()
