import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time

user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
headers = {'User-Agent': user_agent_desktop}

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

def vehicle_link_trimmer(model_link):
    trimmed_link = f'/{model_link.split("/")[-2]}/{model_link.split("/")[-1]}'
    return trimmed_link

def find_models():
    driver = webdriver.Chrome()
    url = 'https://www.autozone.com/shopbymodel'
    model_links = []
    driver.get(url)
    driver.execute_script('document.getElementById("TopHeader").style.display = "none";')
    chunks = driver.find_elements_by_class_name('styles_shopByItem__3suKD')
    for chunk in chunks:
        make = chunk.find_element_by_class_name('globals_az-title-5-medium__34Jxd').text
        print(f'---{make}---')

        try:
            show_all_button = chunk.find_element_by_id('shopRightArrowBtn')
            show_all_button.click()

            models = driver.find_elements_by_class_name('styles_shopItem___iN2A')
            for model in models:
                model_name = model.text
                model_link = model.get_attribute('href')
                trimmed_link = vehicle_link_trimmer(model_link)
                model_links.append(trimmed_link)
                print(f'{model_name} - {model_link}')
                print(f'     => {vehicle_link_trimmer(model_link)}')
            
            back_button = driver.find_element_by_class_name('styles_backIcon__2KGHP')
            back_button.click()
        except NoSuchElementException:
            models = chunk.find_elements_by_class_name('globals_az-body-1-regular__oKXlJ')
            for model in models:
                model_name = model.text
                model_link = model.find_element_by_tag_name('a').get_attribute('href')
                trimmed_link = vehicle_link_trimmer(model_link)
                model_links.append(trimmed_link)
                print(f'{model_name} - {model_link}')
                print(f'     => {vehicle_link_trimmer(model_link)}')
    save_to_file_vehicles(model_links)

def find_categories():
    links_to_check = []
    with open('vehicles.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for each in csvreader:
            each_trimmed = each[0].replace('[', '')
            each_trimmed = each_trimmed.replace(']', '')
            each_trimmed = each_trimmed.replace("'", '')
            link = f'https://www.autozone.com/parts{each_trimmed}'
            links_to_check.append(link)
            print(link)
            
    category_links = []
    for link in links_to_check:
        level_1_soup = getSoup(link, headers)
        level_1_elems = level_1_soup.find_all(
            'div', class_='styles_item__24J6O styles_grid-sm-12__2F5bi styles_grid-lg-6__1GgbN'
            )
        level_1_links = []
        for each in level_1_elems:
            level_1_links.append(f"https://www.autozone.com{each.find('a')['href']}")
            print(f"> {each.find('a')['href']}")

        for level_1_link in level_1_links:
            cut_link = level_1_link.split('/')
            trimmed_link = '/' + '/'.join(cut_link[3:-2])
            if trimmed_link[0:6] != '/parts' and trimmed_link not in category_links:
                category_links.append(trimmed_link)
                print(f'=> {trimmed_link}')

            level_2_soup = getSoup(level_1_link, headers)
            level_2_elems = level_2_soup.find_all(
            'div', class_='styles_item__24J6O styles_grid-sm-12__2F5bi styles_grid-lg-6__1GgbN'
            )
            level_2_links = []
            for each in level_2_elems:
                level_2_links.append(f"https://www.autozone.com{each.find('a')['href']}")
                print(f">> {each.find('a')['href']}")

            for level_2_link in level_2_links:
                cut_link = level_2_link.split('/')
                trimmed_link = '/' + '/'.join(cut_link[3:-2])
                if trimmed_link[0:6] != '/parts' and trimmed_link not in category_links:
                    category_links.append(trimmed_link)
                    print(f'==> {trimmed_link}')

                level_3_soup = getSoup(level_2_link, headers)
                level_3_elems = level_3_soup.find_all(
                'div', class_='styles_item__24J6O styles_grid-sm-12__2F5bi styles_grid-lg-6__1GgbN'
                )
                level_3_links = []
                for each in level_3_elems:
                    level_3_links.append(f"https://www.autozone.com{each.find('a')['href']}")
                    print(f">>> {each.find('a')['href']}")

                for level_3_link in level_3_links:
                    cut_link = level_3_link.split('/')
                    trimmed_link = '/' + '/'.join(cut_link[3:-2])
                    if trimmed_link[0:6] != '/parts' and trimmed_link not in category_links:
                        category_links.append(trimmed_link)
                        print(f'===> {trimmed_link}')
        save_to_file_categories(category_links)

find_models()
# find_categories()