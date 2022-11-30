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
    make_container = main_soup.find('ul', id='nav').find('li')
    makes = make_container.find_all('a', href=True)
    for make in makes:
        make_url = make['href']
        make_soup = getSoup(f'https://www.goapr.com{make_url}', headers)
        if make_soup.find('ul', class_='linkedCategories'):
            model_container = make_soup.find('ul', class_='linkedCategories')
        elif make_soup.find('ul', id='platformGridPlaceholder'):
            model_container = make_soup.find('ul', id='platformGridPlaceholder')
        models = model_container.find_all('a', href=True)
        for model in models:
            model_url = model['href']
            trimmed_url = model_url[:-1]
            if trimmed_url not in vehicle_links:
                vehicle_links.append(trimmed_url)
                print(f'> {trimmed_url}')
    save_to_file_vehicles(vehicle_links)

def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'https://www.goapr.com{each_trimmed}/'
            links_to_check.append(link)
            print(link)

    driver = webdriver.Chrome()
    category_links = []
    a = 0
    for link in links_to_check:
        driver.get(link)
        driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_id('narrow_results'))
        time.sleep(random.uniform(3, 8))
        driver.find_element_by_id('narrow_results').click()
        time.sleep(random.uniform(3, 8))

        categories = driver.find_elements_by_class_name('category-link')
        b = 0
        for category in categories:
            category.click()
            driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_id('narrow_results'))
            time.sleep(random.uniform(3, 8))
            driver.find_element_by_id('narrow_results').click()
            time.sleep(random.uniform(3, 8))

            if driver.find_elements_by_class_name('category-link'):
                subcategories = driver.find_elements_by_class_name('category-link')
                c = 0
                for subcategory in subcategories:
                    subcategory.click()
                    driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_id('narrow_results'))
                    time.sleep(random.uniform(3, 8))
                    driver.find_element_by_id('narrow_results').click()
                    time.sleep(random.uniform(3, 8))

                    if driver.find_elements_by_class_name('category-link'):
                        subsubcategories = driver.find_elements_by_class_name('category-link')
                        d = 0
                        for subsubcategory in subsubcategories:
                            subsubcategory.click()
                            driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_id('narrow_results'))
                            time.sleep(random.uniform(3, 8))
                            driver.find_element_by_id('narrow_results').click()
                            time.sleep(random.uniform(3, 8))

                            if driver.find_elements_by_class_name('category-link'):
                                subsubsubcategories = driver.find_elements_by_class_name('category-link')
                                e = 0
                                for subsubsubcategory in subsubsubcategories:
                                    subsubsubcategory_url = driver.current_url
                                    trimmed_link = subsubsubcategory_url[:-1]
                                    if trimmed_link not in category_links:
                                        category_links.append(trimmed_link)
                                        print(f'=> {trimmed_link}')
                                    driver.execute_script("window.history.go(-1)")
                                    time.sleep(random.uniform(3, 8))
                                    e += 1
                            else:
                                subsubcategory_url = driver.current_url
                                trimmed_link = subsubcategory_url[:-1]
                                if trimmed_link not in category_links:
                                    category_links.append(trimmed_link)
                                    print(f'=> {trimmed_link}')
                                driver.execute_script("window.history.go(-1)")
                                time.sleep(random.uniform(3, 8))
                                d += 1
                    else:
                        subcategory_url = driver.current_url
                        trimmed_link = subcategory_url[:-1]
                        if trimmed_link not in category_links:
                            category_links.append(trimmed_link)
                            print(f'=> {trimmed_link.split("/")}')
                        driver.execute_script("window.history.go(-1)")
                        time.sleep(random.uniform(3, 8))
                        c += 1

            else:
                category_url = driver.current_url
                trimmed_link = category_url[:-1]
                if trimmed_link not in category_links:
                    category_links.append(trimmed_link)
                    print(f'=> {trimmed_link}')
                driver.execute_script("window.history.go(-1)")
                time.sleep(random.uniform(3, 8))
                b += 1
                
        driver.execute_script('arguments[0].scrollIntoView();', driver.find_element_by_id('narrow_results'))
        time.sleep(random.uniform(3, 8))
        driver.find_element_by_id('narrow_results').click()
        time.sleep(random.uniform(3, 8))
        categories = driver.find_elements_by_class_name('category-link')
        a += 1





        # vehicle_soup = getSoup(link, headers)
        # print('Categories:')
        # cat_container = vehicle_soup.find_all('ul', class_='sub-menu')[1]
        # categories = cat_container.find_all('a', href=True)
        # for category in categories:
        #     category_url = category['href']
        #     category_soup = getSoup(f'{link}{category_url}', headers)
        #     print('SubCategories:')
        #     try:
        #         subcat_container = category_soup.find_all('ul', class_='sub-menu')[1]
        #         subcategories = subcat_container.find_all('a', href=True)
        #         for subcategory in subcategories:
        #             subcategory_url = subcategory['href']
        #             subcategory_soup = getSoup(f'{link}{subcategory_url}', headers)
        #             print('SubSubCategories:')
        #             try:
        #                 sub_subcat_container = subcategory_soup.find_all('ul', class_='sub-menu')[1]
        #                 sub_subcategories = sub_subcat_container.find_all('a', href=True)
        #                 for sub_subcategory in sub_subcategories:
        #                     sub_subcategory_url = sub_subcategory['href']
        #                     sub_subcategory_soup = getSoup(f'{link}{sub_subcategory_url}', headers)
        #                     print(sub_subcategory_soup)
        #                     print('SubSubSubCategories:')
        #                     try:
        #                         subsub_subcat_container = sub_subcategory_soup.find_all('ul', class_='sub-menu')[1]
        #                         subsub_subcategories = subsub_subcat_container.find_all('a', href=True)
        #                         for subsub_subcategory in subsub_subcategories:
        #                             subsub_subcategory_url = subsub_subcategory['href']
        #                             trimmed_url = f'{subsub_subcategory_url[:-1]}'
        #                             if trimmed_url not in category_links:
        #                                 category_links.append(trimmed_url)
        #                                 print(f'=> {trimmed_url}')
        #                     except AttributeError as e:
        #                         trimmed_url = f'{sub_subcategory_url[:-1]}'
        #                         if trimmed_url not in category_links:
        #                             category_links.append(trimmed_url)
        #                             print(f'=> {trimmed_url} from {e}')
        #             except AttributeError as e:
        #                 trimmed_url = f'{subcategory_url[:-1]}'
        #                 if trimmed_url not in category_links:
        #                     category_links.append(trimmed_url)
        #                     print(f'=> {trimmed_url} from {e}')
        #     except AttributeError as e:
        #         trimmed_url = f'{category_url[:-1]}'
        #         if trimmed_url not in category_links:
        #             category_links.append(trimmed_url)
        #             print(f'=> {trimmed_url} from {e}')

main_url = 'https://www.goapr.com/'
site_name = 'goapr'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

# find_vehicles()
find_categories()