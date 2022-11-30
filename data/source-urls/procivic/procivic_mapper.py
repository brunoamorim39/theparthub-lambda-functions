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

def find_vehicles_and_categories():
    vehicle_links = []
    category_urls = []
    main_soup = getSoup(main_url, headers)
    vehicle_container = main_soup.find('ul', class_='nav nav-pills nav-stacked')
    vehicles = vehicle_container.find_all('a', href=True)
    for vehicle in vehicles:
        vehicle_link = vehicle['href']
        trimmed_vehicle_link = vehicle_link.replace('/a/', '/c/').replace('/parts.html', '')
        vehicle_links.append(trimmed_vehicle_link)
        print(f'> {trimmed_vehicle_link}')
        
        vehicle_url = f'https://www.procivic.com{vehicle_link}'
        vehicle_soup = getSoup(vehicle_url, headers)
        cat_container = vehicle_soup.find('div', class_='snippet_in_page_box readable-width')
        cats = cat_container.find_all('a', href=True)
        for cat in cats:
            cat_url = cat['href']
            trimmed_cat_link = f'/{cat_url.split("/")[-1]}'
            if trimmed_cat_link not in category_urls:
                category_urls.append(trimmed_cat_link)
                print(f'=> {trimmed_cat_link}')
    save_to_file_vehicles(vehicle_links)
    save_to_file_categories(category_urls)

main_url = 'https://www.procivic.com/a/m/civic/parts.html'
site_name = 'procivic'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles_and_categories()