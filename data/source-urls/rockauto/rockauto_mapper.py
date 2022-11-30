import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import time
import random

from selenium import webdriver

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

def save_to_file_vehicles(links, trim_ids):
    with open('vehicles.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_url', 'trim_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        i = 0
        for link in links:
            writer.writerow({'vehicle_url': link, 'trim_id': trim_ids[i]})
            i += 1

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_vehicles():
    # driver = webdriver.Chrome()
    vehicle_links = []
    trim_ids = []
    for url in urls:
        # driver.get(url)
        # vehicle_container = driver.find_element_by_id('treeroot[catalog]')
        # vehicles = vehicle_container.find_elements_by_class_name('navlabellink')
        main_soup = getSoup(url, headers)
        vehicle_container = main_soup.find('div', id='treeroot[catalog]')
        vehicles = vehicle_container.find_all('a', class_='navlabellink', href=True)
        for vehicle in vehicles:
            time.sleep(random.uniform(3, 8))
            # vehicle.click()
            # make_id = vehicle.get_attribute('id').replace('navhref', '')
            # year_container = vehicle.find_element_by_id(f'navchildren{make_id}')
            # years = year_container.find_elements_by_class_name('navlabellink')
            make_link = vehicle['href']
            make_id = vehicle['id'].replace('navhref', '')
            make_soup = getSoup(f'{main_url}/{make_link}', headers)
            year_container = make_soup.find('div', id=f'navchildren{make_id}', class_='nchildren')
            print(year_container)
            years = year_container.find_all('a', class_='navlabellink', href=True)
            for year in years:
                time.sleep(random.uniform(3, 8))
                # year.click()
                # year_id = year.get_attribute('id').replace('navhref', '')
                # model_container = year.find_element_by_id(f'navchildren{year_id}')
                # models = model_container.find_elements_by_class_name('navlabellink')
                year_link = year['href']
                year_id = year['id'].replace('navhref', '')
                year_soup = getSoup(f'{main_url}/{year_link}', headers)
                model_container = year_soup.find('div', id=f'navchildren{year_id}', class_='nchildren')
                # print(model_container)
                models = model_container.find_all('a', class_='navlabellink', href=True)
                for model in models:
                    time.sleep(random.uniform(3, 8))
                    # if len(models) > 1:
                    #     model.click()
                    # model_id = model.get_attribute('id').replace('navhref', '')
                    # trim_container = model.find_element_by_id(f'navchildren{model_id}')
                    # trims = trim_container.find_elements_by_class_name('navlabellink')
                    model_link = model['href']
                    model_id = model['id'].replace('navhref', '')
                    model_soup = getSoup(f'{main_url}/{model_link}', headers)
                    trim_container = model_soup.find('div', id=f'navchildren{model_id}', class_='nchildren')
                    # print(trim_container)
                    trims = trim_container.find_all('a', class_='navlabellink', href=True)
                    for trim in trims:
                        # time.sleep(random.uniform(3, 8))
                        # if len(trims) > 1:
                        #     trim.click()
                        # trim_link = trim.get_attribute('href')
                        # trim_id = trim.get_attribute('id').replace('navhref', '')
                        trim_link = trim['href']
                        trim_id = trim['id'].replace('navhref', '')
                        print(f'> {trim_link} | {trim_id}')
                        vehicle_links.append(trim_link)
                        trim_ids.append(trim_id)
    save_to_file_vehicles(vehicle_links, trim_ids)

def find_categories():
    links_to_check = []
    trim_ids = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'{main_url}/{each_trimmed}'
            links_to_check.append(link)

            trimmed_id = each[1].replace('[', '')
            trimmed_id = trimmed_id.replace(']', '')
            trimmed_id = trimmed_id.replace("'", '')
            trim_ids.append(trimmed_id)

            print(f'{link} | {trimmed_id}')
    
    category_links = []
    i = 0
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        cat_container = vehicle_soup.find('div', id=f'navchildren{trim_ids[i]}')
        categories = cat_container.find_all('a', class_='navlabellink', href=True)
        for category in categories:
            category_link = category['href']
            category_id = category['id'].replace('navhref', '')
            category_soup = getSoup(f'{main_url}/{category_link}', headers)
            subcat_container = category_soup.find('div', id=f'navchildren{category_id}')
            subcats = subcat_container.find_all('a', class_='navlabellink', href=True)
            for subcat in subcats:
                subcat_link = subcat['href']
                trimmed_url = f'{subcat_link.split(",")[-2]},{subcat_link.split(",")[-1]}'
                if trimmed_url not in category_links:
                    print(f'=> {trimmed_url}')
                    category_links.append(trimmed_url)
        i += 1
    save_to_file_categories(category_links)

urls= ['https://www.rockauto.com/en/catalog']
main_url = 'https://www.rockauto.com'
site_name = 'rockauto'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_vehicles()
find_categories()