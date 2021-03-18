from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options


# code needed to run selenium, browser path is specific to where u save chromediver
options = Options()
options.headless= True
browser=webdriver.Chrome(options=options,executable_path="c:\\chromedriver.exe")
url = "https://www.straitstimes.com/search?searchkey=resale%20flats"
browser.get(url)
url_list= []
#code to print out the urls after loading more results
css_counter = 2
hdb_flat_crawled = []

#pulling all the urls first using this code
while True :
    running_counter=0
    try:
        css = "#resultdata > div:nth-child("+str(css_counter)+") > a"
        css_counter += 1
        links = browser.find_element_by_css_selector(css)
        url_list.append(links.get_attribute('href'))
        #print(links.get_attribute('href'))



    #error checking to prevent selenium error
    except NoSuchElementException:
        break

for x in url_list:
    urls = x
    options.headless= True
    browser.get(urls)
    try :
        #to produce image for each url
        img= browser.find_element_by_css_selector("#block-system-main > div > div > div > div.media-group.fadecount0 > div > div > figure > picture > img")
        img_url = img.get_attribute("src")

        #to produce title for each url
        title = browser.find_element_by_css_selector("#block-system-main > div > div > div > header > h1")

        #to produce summary for each url
        summary = browser.find_element_by_css_selector('#block-system-main > div > div > div > div.group-ob-readmore > div.field-name-body-linked.field.field-name-body.field-type-text-with-summary.field-label-hidden > div.field-items > div > p:nth-child(1)')

        hdb_flat_dictionary = {
            "img": img_url,
            "title": title.text,
            "summary": summary.text,
            "url": x
        }

        hdb_flat_crawled.append(hdb_flat_dictionary)

    except:
        continue

print(hdb_flat_crawled)

browser.close()