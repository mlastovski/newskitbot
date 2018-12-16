# encoding=utf8
from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re


def pravda():
    data = requests.get("https://pravda.com.ua/", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"})


    encoding = data.encoding if 'charset' in data.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(data.content, "lxml", from_encoding=encoding)

    articles = []

    for post in soup.find("div", {"class": "block_news"}).find_all("div", {"class": "article"}):
        #print(post)
        title_text = post.find("div", {"class": "article__title"}).find("a").get_text()
        title_text = re.sub('\n', '', title_text)
        title_text = re.sub('\t', '', title_text)
        title_text = re.sub('\xa0', ' ', title_text)
        link = post.find("div", {"class": "article__title"}).find("a").get('href')
        if not link.startswith('https://'):
            link = 'https://www.pravda.com.ua' + link
        author = ' '
        date = datetime.now().timestamp() #post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("div").find("p", {"class": "postDate"})
        #date = datetime.now().replace(hour=int(date[0]), minute=int(date[1]))

        #print('here',title_text, link, date, author)

        if title_text and link and author and date:
            article = {
                'title': title_text,
                'words': '',
                'link': link,
                'author': author,
                'date': date
            }
            print(article)
            articles.append(article)

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating
    print(articles)
    return articles

if __name__ == '__main__':
    pravda()

