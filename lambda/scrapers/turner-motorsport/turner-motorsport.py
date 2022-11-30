import json
import requests
from bs4 import BeautifulSoup

######################################
#### Turner Motorsport PN Scraper ####
######################################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']
    
    base_URL = 'https://www.turnermotorsport.com'
    query_url = f'{base_URL}/Search?No=0&Nrpp=10&Ntt={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    container = soup.find('div', id='product-results')
    try:
        listings = container.find_all('div', class_='product-item')
        for listing in listings:
            listing_obj = {}

            product_link = listing.find('a', class_='cleanDesc', href=True)['href']
            product_link_full = f'{base_URL}{product_link}'
            product_name = listing.find('a', class_='cleanDesc', href=True).text.strip()
            try:
                product_photo = listing.find('img')['data-src']
            except (AttributeError, TypeError, KeyError):
                continue
            product_price = listing.find('section', class_='big-price').text.strip().replace(' ', '')

            listing_obj['link'] = product_link_full
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'turner-motorsport.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)