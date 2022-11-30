import requests
from bs4 import BeautifulSoup
import csv
import time

user_agent_desktop = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip',
'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def getSoup(url, header):
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
    url = 'https://parts.toyota.com/'
    vehicle_links = []
    main_soup = getSoup(url, headers)
    model_ranges = main_soup.find_all('a', class_='ModelRange', href=True)
    for range in model_ranges:
        range_link = range['href']
        range_soup = getSoup(f'https://parts.toyota.com{range_link}', headers)
        models = range_soup.find_all('a', class_='Model', href=True)
        for model in models:
            model_link = model['href']
            model_soup = getSoup(f'https://parts.toyota.com{model_link}', headers)
            years = model_soup.find_all('a', class_='Year', href=True)
            for year in years:
                year_link = year['href']
                year_soup = getSoup(f'https://parts.toyota.com{year_link}', headers)
                try:
                    trims = year_soup.find_all('a', class_='Trimlevel', href=True)
                    for trim in trims:
                        trim_link = trim['href']
                        trim_soup = getSoup(f'https://parts.toyota.com{trim_link}', headers)
                        try:
                            drivelines = trim_soup.find_all('a', class_='Driveline', href=True)
                            for driveline in drivelines:
                                driveline_link = driveline['href'][:len(driveline['href']) - 5]
                                print(f'> {driveline_link}')
                                vehicle_links.append(driveline_link)
                                time.sleep(1)
                        except AttributeError as e:
                            trim_link = trim['href'][:len(trim['href']) - 5]
                            print(f'> {trim_link} from {e}')
                            vehicle_links.append(trim_link)
                            time.sleep(1)
                except AttributeError as e:
                    year_link = year['href'][:len(year['href']) - 5]
                    print(f'> {year_link} from {e}')
                    vehicle_links.append(year_link)
                    time.sleep(1)
            time.sleep(1)
        time.sleep(1)
    save_to_file_vehicles(vehicle_links)


def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'https://parts.toyota.com{each_trimmed}.html'
            links_to_check.append(link)
            print(link)
    category_links = []

    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cats = vehicle_soup.find_all('a', class_='qsCategoryLinkItem', href=True)
        for cat in cats:
            cat_url = cat['href']
            cat_soup = getSoup(f'https://parts.toyota.com{cat_url}', headers)
            try:
                subcats = cat_soup.find_all('a', class_='assemblyResultLink center-block', href=True)
                for subcat in subcats:
                    subcat_url = subcat['href']
                    trimmed_link = f"/{subcat_url.split('/')[-3]}/{subcat_url.split('/')[-2]}/{subcat_url.split('/')[-1]}"
                    if trimmed_link not in category_links:
                        category_links.append(trimmed_link)
                        print(f'==> {trimmed_link}')
                        time.sleep(1)
            except AttributeError as e:
                time.sleep(1)
                continue
    save_to_file_categories(category_links)

find_vehicles()
find_categories()