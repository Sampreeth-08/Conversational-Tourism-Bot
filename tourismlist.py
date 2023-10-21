import os
import sys
import pip._vendor.requests as requests
import bs4
from bs4 import BeautifulSoup
import re
import warnings
import time
import codecs
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument("--log-level=3")
options.add_argument("--window-size=1920,1080")

chrome_driver = r"C:/users/arivappa/documents/seleniumDrivers/chromedriver_106.exe"
# ser = Service(chrome_driver)
# driver = webdriver.Chrome(service=ser, options=options)
driver = webdriver.Chrome(executable_path=chrome_driver, options=options)

indexCounter = 1

def get_attractions(url):
    attractions_url = url[:-6] + "/attractions.html"
    destination_name = url[76:-6]
    driver.get(attractions_url)
    # print("Loaded " + attractions_url)
    # print(destination_name)
    innerHTML = driver.page_source
    soup = BeautifulSoup(innerHTML, 'html.parser')
    # time.sleep(2)
    # print("Sleep completed.........")

    elements = soup.find('div', attrs={'class': 'row attraction-search-lists'})
    if not elements:
        notfound_file = open('notfound.txt', 'a')
        notfound_file.write(attractions_url + "\n")
        notfound_file.close()
        print("Not Found " + destination_name + " ...")
        return

    for kk, alphabetList in enumerate(soup.find_all('div', attrs={'class': 'row attraction-search-lists'})):
        for i, row in enumerate(alphabetList.find_all('div', attrs={'class': 'col-md-4 attraction-list-item spiritual show'})):
            try:
                link_part = row.find(href=True)
                link = link_part['href']
                attraction_link = "https://www.incredibleindia.org" + link
                attraction_name = attraction_link[76 + len(destination_name) + 1 : -5]

                driver.get(attraction_link)
                innerHTML = driver.page_source
                soup = BeautifulSoup(innerHTML, 'html.parser')
                section_div_soup = soup.find('div', attrs={'class': 'section destination-detail'})

                if section_div_soup:
                    attr_file = open('attractions/' + attraction_name + ".txt", "w", encoding="utf-8")
                    writing_string = ""
                    writing_string += destination_name + " \n"
                    writing_string += attraction_name + " \n"
                else:
                    notfound_file = open('notfound.txt', 'a')
                    notfound_file.write(attraction_link + "\n")
                    notfound_file.close()
                    continue

                for k, paragraph in enumerate(section_div_soup.find_all('p')):
                    text = paragraph.text
                    text = text.lower()
                    text = text.replace("\n", " ")
                    text = text.replace("\t", " ")
                    text = text.strip()
                    writing_string += text + " \n"
                
                attr_file.write(writing_string)
                attr_file.close()
            except KeyboardInterrupt:
                print('Interrupted')
                print(KeyboardInterrupt)
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            except Exception:
                print("EXCEPTION ---------------------")
                traceback.print_exc()
    print("completed " + destination_name + " ...")


links_file = open('links.txt', 'r')
links = links_file.readlines()
for link in links:
    get_attractions(link)
