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
    url = 'https://www.moparpartsgiant.com/sitemap.html'
    vehicle_links = []
    sitemap_soup = getSoup(url, headers)
    vehicle_containers = [
        sitemap_soup.find_all('ul', class_='flex-row col-top flex-wrap content')[1],
        sitemap_soup.find_all('ul', class_='flex-row col-top flex-wrap content')[2],
        sitemap_soup.find_all('ul', class_='flex-row col-top flex-wrap content')[3],
        sitemap_soup.find_all('ul', class_='flex-row col-top flex-wrap content')[4]
    ]
    vehicles = []
    for container in vehicle_containers:
        vehicle_elements = container.find_all('a', class_='link', href=True)
        for element in vehicle_elements:
            vehicle_tag = f'https://www.moparpartsgiant.com' + element['href']
            vehicles.append(vehicle_tag)

    for each_vehicle in vehicles:
        vehicle_soup = getSoup(each_vehicle, headers)
        years_container = vehicle_soup.find('div', class_='ab-link-list-content ab-link-list-col4')
        years = years_container.find_all('a', href=True)
        for year in years:
            year_url = year['href']
            if year_url not in vehicle_links:
                print(f'> {year_url}')
                vehicle_links.append(year_url)
    save_to_file_vehicles(vehicle_links)

def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'{main_url}{each_trimmed}'
            links_to_check.append(link)
            print(link)
    
    category_links = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cat_items = vehicle_soup.find_all('a', class_='pr-cg-sub-link', href=True)
        for item in cat_items:
            item_url = item['href']
            trimmed_url = f'/{item_url.split("/")[-2]}/{item_url.split("/")[-1]}'
            if trimmed_url not in category_links:
                category_links.append(trimmed_url)
                print(f'=> {trimmed_url}')
    save_to_file_categories(category_links)

main_url = 'https://www.moparpartsgiant.com'
site_name = 'moparpartsgiant'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles()
find_categories()