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

def find_vehicles():
    vehicle_links = []
    for url in urls:
        main_soup = getSoup(url, headers)
        try:
            vehicle_container = main_soup.find('div', id='vehicle-data-lists')
            vehicles = vehicle_container.find_all('a', href=True)
            for vehicle in vehicles:
                model_link = vehicle['href']
                model_soup = getSoup(f'{main_url}/{model_link}', headers)
                try:
                    year_container = model_soup.find('div', id='vehicle-data-lists')
                    years = year_container.find_all('a', href=True)
                    for year in years:
                        year_link = year['href']
                        year_soup = getSoup(f'{main_url}/{year_link}', headers)
                        try:
                            trim_container = year_soup.find('div', id='vehicle-data-lists')
                            trims = trim_container.find_all('a', href=True)
                            for trim in trims:
                                trim_link = trim['href']
                                print(f'> {trim_link}')
                                vehicle_links.append(trim_link)
                        except AttributeError as e:
                            print(f'> {year_link} from {e}')
                            vehicle_links.append(year_link)
                except AttributeError as e:
                    print(f'> {model_link} from {e}')
                    vehicle_links.append(model_link)
        except AttributeError as e:
            print(e)
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
        cat_container = vehicle_soup.find('div', class_='category-list')
        try:
            category_units = cat_container.find_all('li')
        except AttributeError as e:
            print(e)
            pass
        categories = []
        for each in category_units:
            categories.append(each.find('a', href=True))
        for category in categories:
            cat_url = category['href']
            trimmed_url = f"/{cat_url.split('/')[-1]}"
            if trimmed_url not in category_links:
                print(f'=> {trimmed_url}')
                category_links.append(trimmed_url)
    save_to_file_categories(category_links)

urls= [
    'https://www.overstockmopar.com/v-chrysler',
    'https://www.overstockmopar.com/v-dodge',
    'https://www.overstockmopar.com/v-jeep',
    'https://www.overstockmopar.com/v-ram',
    'https://www.overstockmopar.com/v-srt-viper'
    ]
main_url = 'https://www.overstockmopar.com'
site_name = 'overstockmopar'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

# find_vehicles()
find_categories()