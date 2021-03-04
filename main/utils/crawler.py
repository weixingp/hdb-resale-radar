# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from itertools import chain

import requests
from bs4 import BeautifulSoup


def getdata(url):
    r = requests.get(url)
    return r.text

URL = 'https://mothership.sg/2021/03/tempered-glass-kitchen-shatter/'
page = requests.get(URL)
soup = BeautifulSoup(page.text, 'html.parser')


for item2 in soup.find_all('figure', class_='featured-image'):
    image = item2.img['src']
    print(image)

empty_list = []

for item2 in soup.find_all('title'):
    print(item2.string)

for item2 in soup.find_all('p'):
    if item2.string is not None:
        if len(item2.string) > 100:
            y = item2.string.split()[:]
            empty_list.append(y)

final = list(chain.from_iterable(empty_list))
final = final[:100]
print(' '.join(final) + "...")
