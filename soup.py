#-*-coding:utf-8-*-
import urllib.request
from bs4 import BeautifulSoup as bs 
import sys
import time
import requests
import lxml

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}


def umsist():
    url="https://www.donga.com/news/Society/article/all/20200825/102632158/1?ref=main"
    html = requests.get(url)
    html.encoding = None
    soup = bs(html.text, 'html.parser')
    for line in soup.select('span.date01'):
        print(line)
if __name__ == '__main__':

    umsist()
