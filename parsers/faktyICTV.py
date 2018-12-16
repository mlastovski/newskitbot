from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re

def faktyictv():
    data = requests.get("https://fakty.ictv.ua/ua").text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find("div", {"class": "last_blogroll_news"}).find("ul").find_all("li"):
        title_text = title.find("a").get_text()
        title_text = re.sub('\xa0', ' ', title_text)
        #print(title_text)
        link = title.find("a").get("href")
        #print(link)
        author = ' '
        date = datetime.now().timestamp()

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

    return articles

if __name__ == '__main__':
    faktyictv()
