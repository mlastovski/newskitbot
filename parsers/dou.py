from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re





def dou():
    data = requests.get("https://dou.ua/lenta/", headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for post in soup.find("div", {"class": "m-cola"}).find("div", {"class": "b-lenta"}).find_all("article", {"class": "b-postcard"}):
        #print(post)
        title_text = post.find("h2").find("a").get_text()
        title_text = re.sub('\n', '', title_text)
        title_text = re.sub('\t', '', title_text)
        title_text = re.sub('\xa0', ' ', title_text)
        link = post.find("h2").find("a").get('href')
        author = ' '
        date = datetime.now().timestamp() #post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("div").find("p", {"class": "postDate"})
        #date = datetime.now().replace(hour=int(date[0]), minute=int(date[1]))

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

if __name__ == '__main__':
    dou()

