from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime

def korrespondent():
    data = requests.get("https://korrespondent.net/").text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find("div", {"class": "time-articles"}).find_all("div", {"class": "article"}):
        title_text = title.find("div", {"class": "article__title"}).find("a").get_text()
        #print(title_text)
        link = title.find("div", {"class": "article__title"}).find("a").get("href")
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
    korrespondent()
