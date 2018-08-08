from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime

def onehundredtwelve():
    data = requests.get("https://112.ua", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)

    soup = BeautifulSoup(data, "lxml")
    
    articles = []

    for title in soup.find("div", {"class": "tabs-panel"}).find("ul", {"class": "tabs-news-list"}).find_all("li"):
        try:
            title_text = title.find("a").get_text()
            # print(title_text)
            link = title.find("a").get("href")
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
            pass

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles 

if __name__ == '__main__':
    onehundredtwelve()
