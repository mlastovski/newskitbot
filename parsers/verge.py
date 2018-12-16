# coding: utf8
from bs4 import BeautifulSoup
import requests
import lxml
from datetime import datetime
import re
import collections
from parsers.parse_tool import extract_keywords

debug = False
test = True

def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )


def verge():
    # getting data
    data = requests.get("https://www.theverge.com/", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)
    soup = BeautifulSoup(data, "lxml")
    articles = []

    for title in soup.find('div', {'class': 'l-main-content'}).find('div', {'class': 'l-col__main'}).find('div').find_all('div'):
        try:
            # print('1')
            title_text = title.find('div', {'class': 'c-entry-box--compact'}).find('div', {'class': 'c-entry-box--compact__body'}).find('h2').find('a').get_text()
            #print(title_text)
            link = title.find('div', {'class': 'c-entry-box--compact'}).find('a').get('href')
            #print(link)
            try:
                structure = requests.get(link, headers={
                    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
            except:
                print('Pass through error!')
            eachpagesoup = BeautifulSoup(structure, "lxml")

            whole_article_text = []
            for eachpage in eachpagesoup.find_all('p'):
                try:
                    article_text = eachpage.get_text()
                    article_text.encode('ascii', 'ignore')
                    # article_text = ''.join(e for e in article_text if e.isalnum())
                    article_text = re.sub('\W+', ' ', article_text)
                    article_text = article_text.lower()
                    article_text = article_text.split(' ')
                    article_text = [str(i) for i in article_text]
                    whole_article_text += article_text
                except UnicodeEncodeError:
                    print("FIGNYA")

            #print(whole_article_text)

            final_text = extract_keywords(whole_article_text, 'en')

            #print(final_text)

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





        except AttributeError:
            continue

    articles = [i for n, i in enumerate(articles) if i not in articles[n + 1:]]  # remove repeating
    return articles

if __name__ == '__main__':
    verge()
