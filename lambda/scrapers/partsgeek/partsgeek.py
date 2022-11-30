import json
import requests
from bs4 import BeautifulSoup

##############################
#### PartsGeek PN Scraper ####
##############################
def lambda_handler(event, context):
    headers = json.loads(event)['headers']
    proxies = json.loads(event)['proxies']
    part_number = json.loads(event)['part_number']

    # DEBUG PARAMS
    # headers = event['headers']
    # proxies = event['proxies']
    # part_number = event['part_number']

    base_URL = 'https://www.partsgeek.com'
    query_url = f'{base_URL}/ss/?i=1&ssq={part_number}'
    resp = requests.get(query_url, proxies=proxies, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    results_array = []
    try:
        container = soup.find('div', class_='products-container')
        listings = container.find_all('div', class_='dp-product')
        for listing in listings:
            listing_obj = {}

            product_name = listing.find('div', class_='product-title').text.strip()
            try:
                product_photo = listing.find('img', class_='pg-image-popover')['src']
            except (AttributeError, TypeError, KeyError):
                continue
            product_price = listing.find('span', class_='product-price').text.strip()

            listing_obj['link'] = resp.url
            listing_obj['name'] = product_name
            listing_obj['image'] = product_photo
            listing_obj['price'] = product_price
            listing_obj['source'] = 'partsgeek.png'

            results_array.append(listing_obj)
    except AttributeError:
        pass
    return json.dumps(results_array)