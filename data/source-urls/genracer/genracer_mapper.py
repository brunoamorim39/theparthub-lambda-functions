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

def save_to_file_vehicles(links, cat_links):
    with open('vehicles_and_categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_url', 'category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        i = 0
        for link in links:
            writer.writerow({'vehicle_url': link, 'category_url': cat_links[i]})
            i += 1

def find_vehicles_and_categories():
    vehicle_links = []
    category_links = []
    main_soup = getSoup(main_url, headers)
    # vehicles_cont = main_soup.find('ul', class_='navList subcategory-grid')
    # print(main_soup)
    vehicles = main_soup.find_all('a', class_='navList-action')
    for vehicle in vehicles:
        vehicle_href = vehicle['href']
        trimmed_vehicle_url = f'/{vehicle_href.split("/")[-2]}'
        vehicle_soup = getSoup(vehicle_href, headers)
        # cat_cont = vehicle_soup.find('ul', class_='navList subcategory-grid')
        cats = vehicle_soup.find_all('a', class_='navList-action')
        for cat in cats:
            cat_href = cat['href']
            trimmed_cat_url = f'/{cat_href.split("/")[-2]}'
            if trimmed_cat_url not in category_links:
                vehicle_links.append(trimmed_vehicle_url)
                category_links.append(trimmed_cat_url)
                print(f'> {trimmed_vehicle_url} | {trimmed_cat_url}')
    save_to_file_vehicles(vehicle_links, category_links)

main_url = f'https://www.genracer.com/vehicle-specific'
site_name = 'genracer'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles_and_categories()