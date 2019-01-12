from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
from parsers.parse_tool import extract_keywords

def hromadske():
    # print('success')
    # getting data
    data = requests.get("https://hromadske.ua/news", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)
    soup = BeautifulSoup(data, "lxml")
    articles = []

    for title in soup.find('div', {'class': 'wrapper'}).find_all('div', {'class': 'item-wrapper'}):
        try:
            # print('success')
            title_text = title.find('a').find('div', {'class': 'title'}).get_text()
            #print(title_text)
            link = title.find('a').get('href')
            if not link.startswith('https://'):
                link = 'https://hromadske.ua' + link
            #print(link)

            try:
                structure = requests.get(link, headers={
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
                # print(structure)
            except:
                print('Pass through error!')

            eachpagesoup = BeautifulSoup(structure, "lxml")
            # print(eachpagesoup)

            final_words = []

            try:
                for eachpage in eachpagesoup.find('div', {'class': 'body-container'}).find_all('p'):
                    try:
                        article_text = eachpage.get_text()
                        #print(article_text)
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

                final_text = extract_keywords(final_words, 'ua')
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

        except AttributeError:
            print('AttributeError')

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating
    if len(articles) < 6:
        try:
            from bot import TOKEN2
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN2, 'Проблема з парсингом Hromadske'))
            requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=373407132&text={}'.format(TOKEN2, 'Проблема з парсингом Hromadske'))
        except ImportError:
            print("Import error (token), can't send message to bot")

    print(len(articles), articles)
    return articles


if __name__ == '__main__':
    hromadske()
