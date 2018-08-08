from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re

def hromadske():
    # print('2')
    data = requests.get("https://hromadske.ua", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find("div", {"class": "program_time_list"}).find_all("a", {"class": "item"}):
        title_text = title.find("div", {"class": "text"}).get_text()
        title_text = re.sub('\xa0', ' ', title_text)
        link = 'https://hromadske.ua' + title.get('href')
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

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles

if __name__ == '__main__':
    hromadske()
