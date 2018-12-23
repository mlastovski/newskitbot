from bs4 import BeautifulSoup
import requests
import lxml
import re
from parsers.parse_tool import extract_keywords

def faktyictv():
    data = requests.get("https://fakty.ictv.ua/ua").text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for title in soup.find("div", {"class": "last_blogroll_news"}).find("ul").find_all("li"):
        try:
            title_text = title.find("a").get_text()
            title_text = re.sub('\xa0', ' ', title_text)
            # print(title_text)
            link = title.find("a").get("href")
            # print(link)

            try:
                structure = requests.get(link, headers={
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                print('Pass through error!')

            eachpagesoup = BeautifulSoup(structure, "lxml")

            final_words = []

            for eachpage in eachpagesoup.find_all('p'):
                try:
                    article_text = eachpage.get_text()
                    article_text.encode('ascii', 'ignore')
                    # article_text = ''.join(e for e in article_text if e.isalnum())
                    article_text = re.sub('\W+', ' ', article_text)
                    article_text = article_text.lower()
                    article_text = article_text.split(' ')
                    article_text = [str(i) for i in article_text]
                    final_words += article_text
                    # print(final_words)
                    # print(article_text)
                except UnicodeEncodeError and AttributeError:
                    print("FIGNYA")

            final_text = extract_keywords(final_words, 'ua')
            # print(final_text)
            date = ' '
            author = ' '


            if title_text and link and author and date and final_text:
                article = {
                    'title': title_text,
                    'words': final_text,
                    'link': link,
                    'author': author,
                    'date': date
                }
                print(article)
                articles.append(article)

        except AttributeError:
            try:
                from bot import TOKEN
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Проблема з парсингом faktyICTV'))
            except ImportError:
                print("Import error (token), can't send message to bot")
                continue


    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles

if __name__ == '__main__':
    faktyictv()
