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
    urls = ['https://www.enjukuracing.com/categories/nissan/', 'https://www.enjukuracing.com/categories/other-makes/']
    vehicle_links = []
    category_links = []
    for url in urls:
        main_soup = getSoup(url, headers)
        vehicles = main_soup.find_all('a', class_='image-link', href=True)
        for vehicle in vehicles:
            vehicle_url = vehicle['href']
            vehicle_soup = getSoup(vehicle_url, headers)
            gens_or_cats = vehicle_soup.find_all('a', class_='image-link', href=True)
            for item in gens_or_cats:
                item_url = item['href']
                item_soup = getSoup(item_url, headers)
                if item_soup.find('ul', class_='sub-category-list'):
                    cats = item_soup.find_all('a', class_='image-link', href=True)
                    for cat in cats:
                        cat_url = cat['href']
                        cat_soup = getSoup(cat_url, headers)
                        if cat_soup.find('ul', class_='sub-category-list'):
                            subcats = cat_soup.find_all('a', class_='image-link', href=True)
                            for subcat in subcats:
                                subcat_url = subcat['href']
                                trimmed_url = subcat_url.split("/")[3:-3]
                                trimmed_url = '/'.join(trimmed_url)
                                trimmed_url = '/' + trimmed_url
                                if trimmed_url not in vehicle_links:
                                    vehicle_links.append(trimmed_url)
                                    print(f'> {trimmed_url}')
                                cat_url = '/' + subcat_url.split('/')[-4] + '/' + subcat_url.split('/')[-3] + '/' + subcat_url.split('/')[-2]
                                if cat_url not in category_links:
                                    category_links.append(cat_url)
                                    print(f'=> {cat_url}')

                        elif cat_soup.find('ul', class_='productGrid'):
                            trimmed_url = cat_url.split("/")[3:-3]
                            trimmed_url = '/'.join(trimmed_url)
                            trimmed_url = '/' + trimmed_url
                            if trimmed_url not in vehicle_links:
                                vehicle_links.append(trimmed_url)
                                print(f'> {trimmed_url}')
                            cat_url = '/' + cat_url.split('/')[-3] + '/' + cat_url.split('/')[-2]
                            if cat_url not in category_links:
                                category_links.append(cat_url)
                                print(f'=> {cat_url}')
                elif item_soup.find('ul', class_='productGrid'):
                    trimmed_url = item_url.split("/")[3:-2]
                    trimmed_url = '/'.join(trimmed_url)
                    trimmed_url = '/' + trimmed_url
                    if trimmed_url not in vehicle_links:
                        vehicle_links.append(trimmed_url)
                        print(f'> {trimmed_url}')
                    cat_url = '/' + item_url.split('/')[-2]
                    if cat_url not in category_links:
                        category_links.append(cat_url)
                        print(f'=> {cat_url}')
    save_to_file_vehicles(vehicle_links)
    save_to_file_categories(category_links)

main_url = 'https://www.enjukuracing.com/'
site_name = 'enjukuracing'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles()