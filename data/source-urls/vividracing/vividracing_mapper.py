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

def save_to_file_ref_vehicles(links):
    with open('ref_vehicles.csv', 'w', newline='') as csvfile:
        fieldnames = ['vehicle_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'vehicle_url': link})

def save_to_file_vehicles(class8, class9):
    with open('vehicles.csv', 'w', newline='') as csvfile:
        fieldnames = ['class8', 'class9']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        i = 0
        for each in range(len(class8)):
            writer.writerow({'class8': class8[i],'class9': class9[i]})
            i += 1

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

def find_vehicles():
    driver = webdriver.Firefox()
    vehicle_urls = []
    driver.get(main_url)
    time.sleep(random.uniform(10, 15))
    driver.find_element_by_class_name('mc-closeModal').click()
    vehicle_selector = driver.find_element_by_id('vehicleSelector')
    make_box = vehicle_selector.find_elements_by_class_name('btn-block')[0]
    model_box = vehicle_selector.find_elements_by_class_name('btn-block')[1]
    year_box = vehicle_selector.find_elements_by_class_name('btn-block')[2]

    make_box.click()
    makes_list = vehicle_selector.find_elements_by_class_name('dropdown-menu')[0]
    makes = makes_list.find_elements_by_tag_name('a')
    for make in makes:
        driver.execute_script('arguments[0].scrollIntoView();', make)
        make.click()
        driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_tag_name('body'))
        time.sleep(random.uniform(1, 2))
        model_box.click()
        models_list = vehicle_selector.find_elements_by_class_name('dropdown-menu')[1]
        models = models_list.find_elements_by_tag_name('a')
        for model in models:
            driver.execute_script('arguments[0].scrollIntoView();', model)
            model.click()
            driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_tag_name('body'))
            time.sleep(random.uniform(1, 2))
            year_box.click()
            years_list = vehicle_selector.find_elements_by_class_name('dropdown-menu')[2]
            years = years_list.find_elements_by_tag_name('a')
            for year in years:
                driver.execute_script('arguments[0].scrollIntoView();', year)
                year_url = year.get_attribute('href')
                driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_tag_name('body'))
                if year_url not in vehicle_urls:
                    vehicle_urls.append(year_url)
                    print(f'> {year_url}')
            model_box.click()
        make_box.click()
    save_to_file_ref_vehicles(vehicle_urls)


def find_categories():
    links_to_check = []
    class8s = []
    class9s = []
    with open('ref_vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'{each_trimmed}'
            links_to_check.append(link)
            print(link)
    
    for link in links_to_check:
        link_parts = link[:-5].split('-')
        class8 = link_parts[-2]
        class9 = link_parts[-1]
        if class8 not in class8s:
            class8s.append(class8)
        if class9 not in class9s:
            class9s.append(class9)
    save_to_file_vehicles(class8s, class9s)

    category_urls = []
    for link in links_to_check:
        vehicle_soup = getSoup(link, headers)
        categories = vehicle_soup.find_all('div', class_='col-xs-6 col-sm-3')
        for category in categories:
            category_link = category.find('a', href=True)['href']
            category_soup = getSoup(category_link, headers)
            if category_soup.find_all('a', class_='product-listing', href=True):
                trimmed_url = category_link.split('/')[-1].split('?')[0]
                if trimmed_url not in category_urls:
                    category_urls.append(trimmed_url)
                    print(f'=> {trimmed_url}')
            else:
                subcategories = category_soup.find_all('div', class_='col-xs-6 col-sm-3')
                for subcategory in subcategories:
                    subcategory_link = subcategory.find('a', href=True)['href']
                    subcategory_soup = getSoup(subcategory_link, headers)
                    if subcategory_soup.find_all('a', class_='product-listing', href=True):
                        trimmed_url = subcategory_link.split('/')[-1].split('?')[0]
                        if trimmed_url not in category_urls:
                            category_urls.append(trimmed_url)
                            print(f'==> {trimmed_url}')
                    else:
                        subsubcats = subcategory_soup.find_all('div', class_='col-xs-6 col-sm-3')
                        for subsubcat in subsubcats:
                            subsubcat_link = subsubcat.find('a', href=True)['href']
                            subsubcat_soup = getSoup(subsubcat_link, headers)
                            if subsubcat_soup.find_all('a', class_='product-listing', href=True):
                                trimmed_url = subsubcat_link.split('/')[-1].split('?')[0]
                                if trimmed_url not in category_urls:
                                    category_urls.append(trimmed_url)
                                    print(f'===> {trimmed_url}')
        save_to_file_categories(category_urls)

main_url = 'https://www.vividracing.com/'
site_name = 'vividracing'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

# find_vehicles()
find_categories()