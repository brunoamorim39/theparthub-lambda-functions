import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import time
import random

user_agent_desktop = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip',
'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def sleep_scraper():
    time.sleep(random.uniform(3, 8))
    return

def getSoup(url, header):
    reqCount = 0
    while True:
        if reqCount > 4:
            return
        sleep_scraper()
        try:
            resp = requests.get(url, timeout=10, headers=header)
            soup = BeautifulSoup(resp.content, "html.parser")
            return soup
        except:
            reqCount += 1
            print('Trying again...')
            # traceback.print_exc()
            # headerCookie = getCookie()
            pass

def save_to_file_vehicles(links):
    with open('vehicles.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'vehicle_url': link})

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_vehicles_and_categories():
    vehicle_links = []
    category_links = []
    main_soup = getSoup(main_url, headers)
    main_cont = main_soup.find('div', class_='container-body')
    vehicles_and_cats = main_cont.find('li').find_all('li')
    for item in vehicles_and_cats:
        try:
            cats = item.find('ul').find_all('a', href=True)
        except AttributeError as e:
            print(e)
            pass
        for cat in cats:
            cat_href = cat['href']
            trimmed_vehicle_url = f'/{cat_href.split("/")[3]}'
            if len(cat_href.split('/')) == 7:
                trimmed_cat_url = f'/{cat_href.split("/")[-3]}/{cat_href.split("/")[-2]}'
            else:
                trimmed_cat_url = f'/{cat_href.split("/")[-2]}'
            if trimmed_vehicle_url not in vehicle_links:
                vehicle_links.append(trimmed_vehicle_url)
                print(f'> {trimmed_vehicle_url}')
            if trimmed_cat_url not in category_links:
                category_links.append(trimmed_cat_url)
                print(f'=> {trimmed_cat_url}')
    save_to_file_vehicles(vehicle_links)
    save_to_file_categories(category_links)

main_url = f'https://classicalfa.com/sitemap/categories/#'
site_name = 'classicalfa'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles_and_categories()