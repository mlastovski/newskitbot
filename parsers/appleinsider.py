from bs4 import BeautifulSoup
import requests
import lxml
import re
from parsers.parse_tool import extract_keywords



def appleinsider():
    data = requests.get("https://appleinsider.ru/").text

    soup = BeautifulSoup(data, "lxml")

    articles = []


    for title in soup.find("main", {"class": "site-main"}).find_all('article'):
        try:
            title_text = title.find('header').find('h2').find('a').get_text()
            title_text = re.sub('\n', '', title_text)
            link = title.find('header').find('h2').find('a').get('href')
            # author = ' '
            # date = datetime.now().timestamp()

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

            author = ''
            date = ''


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

            if len(articles) > 5:
                break

        except AttributeError:
            print('AttributeError')


    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating

    if len(articles) < 5:
        try:
            from bot import TOKEN2
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN2, 'Проблема з парсингом Appleinsider'))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN2, 'Проблема з парсингом Appleinsider'))
        except ImportError:
            print("Import error (token), can't send message to bot")

    print(len(articles), articles)
    return articles

if __name__ =='__main__':
    appleinsider()


