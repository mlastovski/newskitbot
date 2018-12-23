from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
from parsers.parse_tool import extract_keywords

mon = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12'
}


def parse_ainua():
    data = requests.get("https://ain.ua/", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text

    soup = BeautifulSoup(data, "lxml")

    articles = []

    for part in soup.find_all("div", {"class": "posts-list"}):
        try:
            for title in part.find_all("div", {"class": "post-item"}):
                try:
                    title_text = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find(
                        "div", {"class": "left-column-top"}).find("h3", {"class": "post-title"}).get_text()
                except AttributeError:
                    # print(title)
                    continue
                title_text = re.sub('\n', '', title_text)
                link = title.find("a", {"class": "post-link"}).get('href')
                author = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find("div", {
                    "class": "left-column-bottom"}).find("div", {"class": "author"}).find('a').get_text().replace('  ',
                                                                                                                  '').replace(
                    '\n', '')
                date = title.find("div", {"class": "post-inner"}).find("div", {"class": "left-column"}).find("div", {
                    "class": "left-column-top"}).find("div", {"class": "category-wrapper"}).find('time').get_text()
                month = date.split(' ')[1].replace(',', '')
                # print(datetime.now().replace(hour=int(date.split(' ')[2].split(':')[0]), day=int(date.split(' ')[0]), minute=int(date.split(' ')[2].split(':')[1]), month=int(mon.get(month))))

                date = datetime.now().timestamp()
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
                print(final_text)

                if title_text and link and author and date:
                    article = {
                        'title': title_text,
                        'words': final_text,
                        'link': link,
                        'author': author,
                        'date': date
                    }
                    # print(article)
                    articles.append(article)

        except AttributeError:
            try:
                from bot import TOKEN
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Проблема з парсингом Ain'))
            except ImportError:
                print("Import error (token), can't send message to bot")
                continue

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]]  # remove repeating

    return articles


if __name__ == '__main__':
    parse_ainua()
