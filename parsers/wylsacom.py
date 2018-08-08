from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
from apscheduler.schedulers.blocking import BlockingScheduler





def wylsa():
    data = requests.get("https://wylsa.com/category/news/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for postsSection in soup.find("section", {"class": "postsFeed"}).find_all("div", {"class": "postsSection"}):
        for post in postsSection.find_all("div", {"class": "card"}):
            #print(post)
            title_text = post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("h3").get_text()
            title_text = re.sub('\n', '', title_text)
            link = post.find('a').get('href')
            author = ' '
            date = datetime.now().timestamp() #post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("div").find("p", {"class": "postDate"})
            #date = datetime.now().replace(hour=int(date[0]), minute=int(date[1]))

            print('here',title_text, link, date, author)

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
    wylsa()

