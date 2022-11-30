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
    time.sleep(random.uniform(10, 15))
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
    vehicle_links = []
    sitemap_soup = getSoup(main_url, headers)
    vehicle_containers = sitemap_soup.find_all('a', class_='seoLinkItem Make', href=True)

    for container in vehicle_containers:
        container_url = 'https://www.moparpartsoverstock.com' + container['href']
        make_soup = getSoup(container_url, headers)
        models = make_soup.find_all('a', class_='seoLinkItem Model', href=True)
        for model in models:
            model_url = 'https://www.moparpartsoverstock.com' + model['href']
            model_soup = getSoup(model_url, headers)
            years = model_soup.find_all('a', class_='seoLinkItem Year', href=True)
            for year in years:
                year_url = 'https://www.moparpartsoverstock.com' + year['href']
                year_soup = getSoup(year_url, headers)
                drivelines = year_soup.find_all('a', class_='seoLinkItem Driveline', href=True)
                for driveline in drivelines:
                    driveline_url = 'https://www.moparpartsoverstock.com' + driveline['href']
                    driveline_soup = getSoup(driveline_url, headers)
                    trims = driveline_soup.find_all('a', class_='seoLinkItem Trimlevel', href=True)
                    for trim in trims:
                        trim_url = trim['href']
                        if trim_url not in vehicle_links:
                            vehicle_links.append(trim_url)
                            print(f'> {trim_url}')
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
        cat_items = vehicle_soup.find_all('a', class_='seoLinkItem Category', href=True)
        for cat in cat_items:
            cat_url = 'https://www.moparpartsoverstock.com' + cat['href']
            cat_soup = getSoup(cat_url, headers)
            subcats = cat_soup.find_all('a', class_='assemblyResultLink center-block', href=True)
            for subcat in subcats:
                subcat_url = subcat['href']
                if subcat_url not in category_links:
                    category_links.append(subcat_url)
                    print(f'=> {subcat_url}')
    save_to_file_categories(category_links)

main_url = 'https://www.moparpartsoverstock.com'
site_name = 'moparpartsoverstock'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles()
find_categories()