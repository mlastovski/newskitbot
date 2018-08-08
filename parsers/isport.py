from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re

def isport():
    data = requests.get("http://isport.ua/news", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find("div", {"class": "news"}).find_all("div", {"class": "article"}):
        try:
            title_text = title.find("div", {"class": "article__title"}).find("a").get_text()
            title_text = re.sub('\n', '', title_text)
            title_text = re.sub('\t', '', title_text)
            # print(title_text)
            link = "http://isport.ua" + title.find("div", {"class": "article__title"}).find("a").get("href")
            # print(link)
            author = ' '
            date = datetime.now().timestamp()

            if title_text and link and author and date:
                article = {
                    'title': title_text,
                    'link': link,
                    'author': author,
                    'date': date
                }
                print(article)
                articles.append(article)
        except AttributeError:
            from bot import TOKEN
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Проблема з парсингом isport.ua'))


    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles

if __name__ == '__main__':
    isport()
