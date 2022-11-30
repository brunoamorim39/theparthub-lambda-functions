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

def save_to_file_categories(links):
    with open('categories.csv', 'w', newline='') as csvfile:
        fieldnames = ['category_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for link in links:
            writer.writerow({'category_url': link})

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
        if vehicle_soup.find('div', id='searchspring-content').text.strip():
            trimmed_url = f'/{link.split("/")[-1]}'
            if trimmed_url not in category_links:
                category_links.append(trimmed_url)
                print(f'> {trimmed_url}')
        else:
            categories = vehicle_soup.find('div', class_='subcategories').find_all('a', href=True)
            for category in categories:
                category_tag = main_url + '/' + category['href']
                category_soup = getSoup(category_tag, headers)
                try:
                    if category_soup.find('div', id='searchspring-content').text.strip():
                        trimmed_url = f'/{category["href"]}'
                        if trimmed_url not in category_links:
                            category_links.append(trimmed_url)
                            print(f'=> {trimmed_url}')
                    else:
                        subcategories = category_soup.find('div', class_='subcategories').find_all('a', href=True)
                        for subcategory in subcategories:
                            subcat_tag = main_url + '/' + subcategory['href']
                            subcategory_soup = getSoup(subcat_tag, headers)
                            if subcategory_soup.find('div', id='searchspring-content'):
                                trimmed_url = f'/{subcategory["href"]}'
                                if trimmed_url not in category_links:
                                    category_links.append(trimmed_url)
                                    print(f'==> {trimmed_url}')
                            else:
                                try:
                                    subsubcats = subcategory_soup.find('div', class_='subcategories').find_all('a', href=True)
                                    for subsubcat in subsubcats:
                                        subsubcat_tag =  main_url + '/' + subsubcat['href']
                                        subsubcat_soup = getSoup(subsubcat_tag, headers)
                                        if subsubcat_soup.find('div', id='searchspring-content').text.strip():
                                            trimmed_url = f'/{subsubcat["href"]}'
                                            if trimmed_url not in category_links:
                                                category_links.append(trimmed_url)
                                                print(f'===> {trimmed_url}')
                                except AttributeError as e:
                                    print(e)
                except AttributeError as e:
                    print(e)

    save_to_file_categories(category_links)
            

main_url = 'https://www.steeda.com'
site_name = 'steeda'

url_file = Path(f'{site_name}-urls.json')
url_file.touch(exist_ok=True)
cat_file = Path(f'{site_name}-cats.json')
cat_file.touch(exist_ok=True)

find_categories()