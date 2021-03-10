# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from itertools import chain
import json
import requests
from urllib import request
from bs4 import BeautifulSoup


def getdata(url):
    r = requests.get(url)
    return r.text

# function needed to deal with nested dictionary of json
def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

#loads the url, puts into beautiful soup and turns into a json dictionary

urlList = ['https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyDuQi378YmI9zlQYBgTNV9ZH50GsiXBXsI&cx=007628173177510673425%3A1wke5kj-ez8&q=allintitle%3A%20hdb&num=10&start=0',
           'https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyDuQi378YmI9zlQYBgTNV9ZH50GsiXBXsI&cx=007628173177510673425%3A1wke5kj-ez8&q=allintitle%3A%20hdb&num=10&start=22',
           'https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyDuQi378YmI9zlQYBgTNV9ZH50GsiXBXsI&cx=007628173177510673425%3A1wke5kj-ez8&q=allintitle%3A%20hdb&num=10&start=44',
           'https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyDuQi378YmI9zlQYBgTNV9ZH50GsiXBXsI&cx=007628173177510673425%3A1wke5kj-ez8&q=allintitle%3A%20hdb&num=10&start=55',
           'https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyDuQi378YmI9zlQYBgTNV9ZH50GsiXBXsI&cx=007628173177510673425%3A1wke5kj-ez8&q=allintitle%3A%20hdb&num=10&start=77']

k = 0
urls = []

for i in urlList:
    html = request.urlopen(urlList[k]).read()
    soup = BeautifulSoup(html, 'html.parser')
    site_json = json.loads(soup.text)
    urls.append(list(findkeys(site_json, 'link')))
    k += 1

j = 0

for i in urls:
    l = 0
    for m in urls[j]:
        URL = urls[j][l]
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')

        for item2 in soup.find_all('figure', class_='featured-image'): #for image
            image = item2.img['src']
            print(image)

        empty_list = []

        for item2 in soup.find_all('title'): #for title
            print(item2.string)

        for item2 in soup.find_all('p'): #for summary
            if item2.string is not None:
                if len(item2.string) > 100:
                    y = item2.string.split()[:]
                    empty_list.append(y)

        final = list(chain.from_iterable(empty_list))
        final = final[:100]
        print(' '.join(final) + "...")
        print()
        l += 1
    j += 1