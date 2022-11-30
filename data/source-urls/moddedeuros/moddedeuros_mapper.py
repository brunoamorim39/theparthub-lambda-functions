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
    vehicle_links = []
    main_soup = getSoup(main_url, headers)
    model_containers = main_soup.find_all('div', class_='shop-by-model__wrapper')
    for container in model_containers:
        models = container.find_all('a', class_='category-list__item__link', href=True)
        for model in models:
            model_url = model['href']
            model_soup = getSoup(f'https://www.moddedeuros.com{model_url}', headers)
            main_content = model_soup.find('div', class_='main-content')
            generations = main_content.find_all('a', class_='category-list__item__link', href=True)
            for generation in generations:
                generation_url = generation['href']
                if generation_url not in vehicle_links and model_containers.index(container) != 2:
                    vehicle_links.append(generation_url)
                    print(f'> {generation_url}')
                else:
                    generation_soup = getSoup(f'https://www.moddedeuros.com{generation_url}', headers)
                    trim_content = generation_soup.find('div', class_='main-content')
                    trims = trim_content.find_all('a', class_='category-list__item__link', href=True)
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
            link = f'https://www.moddedeuros.com{each_trimmed}'
            links_to_check.append(link)
            print(link)

    category_links = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        main_content = vehicle_soup.find('div', class_='main-content')
        categories = main_content.find_all('a', class_='category-list__item__link', href=True)
        for category in categories:
            category_url = category['href']
            category_soup = getSoup(f'https://www.moddedeuros.com{category_url}', headers)
            if category_soup.find('div', class_='products'):
                trimmed_link = f'/{category_url.split("/")[-1]}'
                if trimmed_link not in category_links:
                    category_links.append(trimmed_link)
                    print(f'=> {trimmed_link}')
            subcategory_container = category_soup.find('div', class_='main-content')
            subcategories = subcategory_container.find_all('a', class_='category-list__item__link', href=True)
            for subcategory in subcategories:
                subcat_url = subcategory['href']
                trimmed_link = f'/{subcat_url.split("/")[-2]}/{subcat_url.split("/")[-1]}'
                if trimmed_link not in category_links:
                    category_links.append(trimmed_link)
                    print(f'=> {trimmed_link}')
    save_to_file_categories(category_links)

main_url = 'https://www.moddedeuros.com/'
site_name = 'moddedeuros'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles()
find_categories()