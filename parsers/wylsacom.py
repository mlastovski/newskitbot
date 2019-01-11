from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
from parsers.parse_tool import extract_keywords





def wylsa():
    data = requests.get("https://wylsa.com/category/news/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for postsSection in soup.find("section", {"class": "postsFeed"}).find_all("div", {"class": "postsSection"}):
        try:
            for post in postsSection.find_all("div", {"class": "card"}):
                #print(post)
                title_text = post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("h3").get_text()
                title_text = re.sub('\n', '', title_text)
                link = post.find('a').get('href')
                author = ' '
                date = datetime.now().timestamp() #post.find("a").find("div", {"class": "cardWrapper"}).find("div", {"class": "cardTitle"}).find("div").find("p", {"class": "postDate"})
                #date = datetime.now().replace(hour=int(date[0]), minute=int(date[1]))

                # print('here',title_text, link, date, author)

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
                        # print(article_text)
                    except UnicodeEncodeError:
                        print("FIGNYA")

                final_text = extract_keywords(final_words, 'ru')
                final_text += ' техно'
                # print(final_text)

                if title_text and link:
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
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN,
                                                                                                           'Проблема з парсингом Wylsacom'))
            except ImportError:
                print("Import error (token), can't send message to bot")
                continue


        articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    return articles

if __name__ == '__main__':
    wylsa()

