import requests
from bs4 import BeautifulSoup
import sqlalchemy as db
import json
import time

####################################
#### K&N Filters Product Mapper ####
####################################
VENDOR_NAME = 'knfilters'
BASE_URL = 'https://www.knfilters.com'

with open('../../application/config.json', 'r') as config_file:
    db_config = json.load(config_file)

db_engine = db.create_engine(db_config.get('SQLALCHEMY_DATABASE_URI'))
db_conn = db_engine.connect()
metadata = db.MetaData()
xref_products_table = db.Table('cross_reference_products', metadata, autoload=True, autoload_with=db_engine)

payload = {
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    },
    'proxies': {
        'http': 'http://45.72.59.14:3128'
    }
}
headers = payload['headers']
proxies = payload['proxies']

def db_do_upsert(url, xref, name):
    print(f'{url} | {xref} | {name}')

    query = db.select(xref_products_table).where(xref_products_table.columns.vendor==VENDOR_NAME, xref_products_table.columns.url==url)
    result = db_conn.execute(query).first()

    if result is not None and result[1] == VENDOR_NAME:
        # Check if any changes exist or if we can skip
        if result[2] == url and result[3] == xref and result[4] == name:
            print('No changes found, SKIP')
        else:
            # Build UPDATE operation query
            print('Updating record...')
            upsert_query = db.update(xref_products_table).values(url=url, xref=xref, name=name).where(xref_products_table.columns.vendor==VENDOR_NAME)
            db_conn.execute(upsert_query)
    else:    
        # Build INSERT operation query
        print('Inserting record...')
        upsert_query = db.insert(xref_products_table).values(vendor=VENDOR_NAME, url=url, xref=xref, name=name)
        db_conn.execute(upsert_query)
    return

def get_parts_page(url):
    try:
        resp = requests.get(url, proxies=proxies, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        if soup.find('div', class_='_3IVGv4pwtBqGRn7_UOpz73'):
            return
        part_xref = soup.find('h1', class_='_3Cir9wIlHLMIeTwLLMbCuo').text.strip()
        part_name = soup.find('h1', class_='_1KvJhhAHFQQ2K5USKJ56dc').text.strip()
        db_do_upsert(url, part_xref, part_name)
    except AttributeError:
        time.sleep(10)
        get_parts_page(url)
    

def get_brands_page(url):
    try:
        resp = requests.get(url, proxies=proxies, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        ref_parts = soup.find_all('li', class_='UfDPijIpXyjDv4Su7qLm2')
        for part in ref_parts:
            part_link = part.find('a')['href']
            part_url = f'https://www.knfilters.com{part_link}'
            get_parts_page(part_url)
    except AttributeError:
        time.sleep(10)
        get_brands_page(url)

def get_xref_page(url):
    try:
        resp = requests.get(url, proxies=proxies, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        container = soup.find('ul', class_='-buCiWq97Zwh8K3NM1Mdi')
        brands = container.find_all('li', class_='UfDPijIpXyjDv4Su7qLm2')
        for brand in brands:
            brand_link = brand.find('a')['href']
            brand_url = f'https://www.knfilters.com{brand_link}'
            get_brands_page(brand_url)
    except AttributeError:
        time.sleep(10)
        get_xref_page(url)


query_url = f'{BASE_URL}/cross-reference'
get_xref_page(query_url)