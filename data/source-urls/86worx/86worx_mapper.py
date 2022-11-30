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

def getSoup(url, header):
    time.sleep(random.uniform(3, 8))
    reqCount = 0
    while True:
        if reqCount > 4:
            return
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

def find_vehicles():
    main_soup = getSoup(main_url, headers)
    container = main_soup.find('ul', class_='sitemap')
    vehicles = container.find_all('li', class_='level-0')
    for vehicle in vehicles:
        vehicle_url = vehicle.find('a', href=True)['href']
        trimmed_url = vehicle_url[:-5]
        if trimmed_url not in vehicle_links:
            vehicle_links.append(trimmed_url)
            print(f'> {trimmed_url}')
    save_to_file_vehicles(vehicle_links)

def find_categories():
    main_soup = getSoup(main_url, headers)
    container = main_soup.find('ul', class_='sitemap')

    categories = container.find_all('li', class_='level-1')
    for category in categories:
        category_url = category.find('a', href=True)['href']
        trimmed_url = f"/{category_url[:-5].split('/')[-1]}"
        if trimmed_url not in category_links:
            category_links.append(trimmed_url)
            print(f'=> {trimmed_url}')
            
    subcategories = container.find_all('li', class_='level-2')
    for subcategory in subcategories:
        subcategory_url = subcategory.find('a', href=True)['href']
        trimmed_url = f"/{subcategory_url[:-5].split('/')[-2]}/{subcategory_url[:-5].split('/')[-1]}"
        if trimmed_url not in category_links:
            category_links.append(trimmed_url)
            print(f'==> {trimmed_url}')
    
    save_to_file_categories(category_links)

site_name = '86worx'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

vehicle_links = []
category_links = []

for i in range(7):
    main_url = f'https://www.86worx.com/catalog/seo_sitemap/category/?p={i + 1}'
    print(main_url)
    find_vehicles()
    find_categories()