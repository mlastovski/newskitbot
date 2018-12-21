# coding: utf-8
from bs4 import BeautifulSoup
import requests
import lxml
import re
from parse_tool import extract_keywords

debug = False
test = True

def appleinsideren():
    # getting data
    data = requests.get("https://appleinsider.com/", headers={
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"}).text
    # print(data)
    soup = BeautifulSoup(data, "lxml")
    articles = []

    for title in soup.find('div', {'class': 'content'}):
        print('success')

if __name__ == '__main__':
    appleinsideren()
