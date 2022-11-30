import requests
from bs4 import BeautifulSoup
import time
import random

from application.models import Make, Model, Category, Subcategory, Part, Classification
from application.__init__ import db

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp, image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip',
'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def sleep_scraper():
    time.sleep(random.uniform(10, 15))
    return

def get_soup(url, header):
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

def price_value_check(part, new_price):
    if new_price != part.price:
        print(f'Price updated from {part.price} to {new_price}')
        print()
        part.price = new_price
        db.session.commit()
    else:
        print('No change in item price found')
        print('Checking next part...')
        print()

def price_check():
    localtime = time.asctime(time.localtime(time.time()))
    start_time = time.time()
    print(f'Current Time: {localtime}')
    db_parts_query = Part.query.all()
    print(f'Part Import Duration: {time.time() - start_time} seconds')
    site_names_available = []
    for part in db_parts_query:
        part_url = part.url
        print(part_url)

        site_name = part_url.split('.')[1]
        if site_name not in site_names_available:
            site_names_available.append(site_name)

        try:
            part_soup = get_soup(part_url, headers)

            if site_name == 'fcpeuro':
                current_price = part_soup.find('div', class_='listing__amount').find('span').text
            elif site_name == 'ecstuning':
                current_price = f'${part_soup.find("span", id="price").text}'
            elif site_name == 'urotuning':
                current_price = part_soup.find('span', class_='bold_option_price_display price').text
            elif site_name == 'turnermotorsport':
                current_price = part_soup.find('span', id='price').text
            elif site_name == 'autohausaz':
                current_price = part_soup.find('div', class_='price').text
            elif site_name == '034motorsport':
                current_price = part_soup.find('span', class_='price').text
            # elif site_name == 'urotuning':
            #     current_price = ''
            elif site_name == 'autohausaz':
                current_price = part_soup.find('div', class_='price').text
            elif site_name == 'autozone':
                current_price = part_soup.find('div', class_='b57d9b').text

            price_value_check(part, current_price)
            
        except AttributeError:
            pass
    
    print(site_names_available)

price_check()