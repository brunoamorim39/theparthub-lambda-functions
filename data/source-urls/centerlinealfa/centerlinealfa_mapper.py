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
    vehicle_queries = []
    main_soup = getSoup(main_url, headers)
    vehicles = main_soup.find('select', id='model').find_all('option')[1::]
    for vehicle in vehicles:
        query_string = vehicle['value']
        if query_string not in vehicle_queries:
            vehicle_queries.append(query_string)
            print(f'> {query_string}')
    save_to_file_vehicles(vehicle_queries)

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
    
    category_queries = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cat_panels = vehicle_soup.find_all('div', class_='accessories')
        for panel in cat_panels:
            cats = panel.find_all('a', href=True)
            for cat in cats:
                cat_href = cat['href']
                trimmed_cat = cat_href.split('&')[0][6::]
                if trimmed_cat not in category_queries:
                    category_queries.append(trimmed_cat)
                    print(f'=> {trimmed_cat}')
    save_to_file_categories(category_queries)

main_url = f'https://www.centerlinealfa.com/store'
site_name = 'centerlinealfa'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

# find_vehicles()
find_categories()