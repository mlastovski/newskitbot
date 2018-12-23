from bs4 import BeautifulSoup
import requests
import lxml
#import scrapy
from datetime import datetime
import re
from parsers.parse_tool import extract_keywords

# removing symbols for better understanding words
def remove_bad_characters(list):
    list = [s.replace(',', '') for s in list]
    list = [s.replace(' ', '') for s in list]
    list = [s.replace(':', '') for s in list]
    list = [s.replace(";", '') for s in list]
    list = [s.replace('!', '') for s in list]
    list = [s.replace("'", '') for s in list]
    list = [s.replace("[", '') for s in list]
    list = [s.replace("]", '') for s in list]
    list = [s.replace("{", '') for s in list]
    list = [s.replace("}", '') for s in list]
    list = [s.replace("-", '') for s in list]
    list = [s.replace("_", '') for s in list]
    list = [s.replace("=", '') for s in list]
    list = [s.replace("+", '') for s in list]
    list = [s.replace("|", '') for s in list]
    list = [s.replace("(", '') for s in list]
    list = [s.replace(")", '') for s in list]
    list = [s.replace("*", '') for s in list]
    list = [s.replace(".", '') for s in list]
    list = [s.replace("@", '') for s in list]
    list = [s.replace("#", '') for s in list]
    list = [s.replace("$", '') for s in list]
    list = [s.replace("%", '') for s in list]
    list = [s.replace("&", '') for s in list]
    list = [s.lower() for s in list]
    return list

def spiegelDeutsch():
    data = requests.get("http://www.spiegel.de/").text
    # print(data)

    soup = BeautifulSoup(data, "lxml")

    articles = []
    i=0
    for title in soup.find('div', {'class': 'column-wide'}).find_all('div', {'class': 'teaser'}):
        try:
            title_text = title.find('div').find('h2').find('a').find('span').get_text()
            # print(title_text)
            link = title.find('div').find('h2').find('a').get('href')
            if not link.startswith('https://') or not link.startswith('http://'):
                link = 'http://www.spiegel.de' + link
            # print(link)
            try:
                structure = requests.get(link, headers={"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                pass
                #print('Pass through error!')
            eachpagesoup = BeautifulSoup(structure, "lxml")

            whole_article_text = []
            for eachpage in eachpagesoup.find_all('p'):
                article_text = eachpage.get_text()
                article_text = re.sub('\n', '', article_text)
                article_text = re.sub('\t', '', article_text)
                article_text = re.sub('\xe4', '', article_text)
                article_text = remove_bad_characters(article_text.split(' '))
                whole_article_text += article_text
                #print(article_text)

            final_text = extract_keywords(whole_article_text, 'de')
            # final_text = extract_keywords(whole_article_text, 'en')
            #print(final_text)

            author = ' '
            date = datetime.now().timestamp()

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
            i+=1
            if i > 3:
                print('ParseError')
                from bot import TOKEN
                requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id=138918380&text={}'.format(TOKEN, 'Проблема з парсингом isport.ua'))


    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]] #remove repeating
    print(articles)
    return articles

if __name__ == '__main__':
    spiegelDeutsch()
