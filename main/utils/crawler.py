# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from itertools import chain

import requests
from bs4 import BeautifulSoup
import re
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
import time

# code needed to run selenium, browser path is specific to where u save chromediver
browser=webdriver.Chrome(executable_path="c:\\chromedriver.exe")
url = "https://mothership.sg/search/?s=resale+flat"
browser.get(url)
page_number = 1
urls = []


def getdata(url):
    r = requests.get(url)
    return r.text

#code to press the button load more results for mothership
while True:
    #try block helps to click the load more results, page number is set to prevent errors where load more results keeps going
    try:
        button = browser.find_element_by_css_selector("#load-more")
        button.click()
        time.sleep(2)
        page_number +=1
        if page_number == 9 :
            break

    #error checking so that no error occurs
    except NoSuchElementException:
        break

#code to print out the urls after loading more results
css_counter = 1
while True :
    try:
        css = "#search-results > div:nth-child(" +str(css_counter)+") > div.ind-article > div > div.header > h1 > a"
        css_counter += 1
        links = browser.find_element_by_css_selector(css)
        urls.append(links.get_attribute('href'))

    #error checking to prevent selenium error
    except NoSuchElementException:
        break




#converts the selenium into a soup obj
#innerHTML = button.execute_script("return document.body.innerHTML")
# web_soup = BeautifulSoup(browser, "html.parser")
#
# # code used ot scrape out the urls
# for x in web_soup.findAll('div',{"class": "header"}):
#     link = x.find('a',href=True)
#     if link is None:
#         continue
#     print(link['href'])


browser.close()

j = 0

for i in urls:
    URL = urls[j]
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
    j += 1

print(urls)